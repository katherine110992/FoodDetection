import sys
import time

import twitter

from food_detector.food_detector_service import FoodDetectorService
from u_logging.logging import Logging


class NetworkAnalysisTwitter:
    """
    :Date: 2017-06-18
    :Version: 0.3
    :Author: CAOBA -Pontificia Universidad Javeriana
    :Copyright: To define
    :Organization: Centro de Excelencia y ApropiaciÃ³n de Big Data y Data Analytics - CAOBA

    This class generates a connection to Twitter and extract information from there. Besides
    the connection and streaming process, the extracted data is sent to the semi structured database and queue.

    """

    def __init__(self, access_credentials):
        """

        :Date: 2017-05-10
        :Version: 0.2
        :Author: CAOBA - Pontificia Universidad Javeriana

        This is the constructor method for the class in which the database and queue connection is made. It also the
        authorization object for Twitter authentication purposes.

        :param access_credentials: needed credentials for Twitter connection
        :type access_credentials: dict

        """
        try:
            self.threadOn = True
            self.costumer_key = access_credentials['costumer_key']
            self.customer_secret = access_credentials['customer_secret']
            self.oauth_token = access_credentials['oauth_token']
            self.oauth_token_secret = access_credentials['oauth_token_secret']
            auth = twitter.oauth.OAuth(self.oauth_token, self.oauth_token_secret, self.costumer_key,
                                       self.customer_secret)
            self._API_TWITTER = twitter.Twitter(auth=auth)
            self.food_detector = FoodDetectorService()
        except:
            Logging.write_standard_error(sys.exc_info())

    def _twitter_api(self, renew):
        """
        :Date: 2017-05-10
        :Version: 0.1
        :Author: CAOBA - Pontificia Universidad Javeriana

        This function generates the connection to Twitter. It has different exceptions in case there is a problem
        with the connection.x

        :param renew: Parameter to initialize the connection to twitter or restart it.
        :type renew: bool

        """
        if self._API_TWITTER is None or renew is True:
            try:
                auth = twitter.oauth.OAuth(self.oauth_token, self.oauth_token_secret, self.costumer_key,
                                           self.customer_secret)
                self._API_TWITTER = twitter.Twitter(auth=auth)
                return True
            except Exception as exc:
                Logging.write_specific_error("Error Connection Twitter OAuth " + str(exc))
                return False
        else:
            Logging.write_success_message("OK Connection Twitter OAuth")
            return True

    def twitter_streaming(self, query, location_api):
        """
        :Date: 2017-06-18
        :Version: 0.2
        :Author: CAOBA - Pontificia Universidad Javeriana.

        This method downloads tweets from Twitter and save them into the semi structured database and queue, according
        to the filters received. The streaming is done by location or by a particular word.
        See https://dev.twitter.com/docs/streaming-apis

        :param query: filter words, comma-separated list of terms. For example: 'Colombia,Peru,Ecuador'
        :type query: str

        :param location_api: Coordinates of a squared located on the particular geographic zone from which the tweets
        will be taken. Must contain two points with latitude and longitude. For example:
        '-81.728111,-4.2304,-66.869827,13.39029'
        :type location_api: str
        """

        reconnect = 0
        try:
            while self.threadOn:
                try:
                    Logging.write_success_message('Filtering query: ' + query + ' and location: ' + location_api)
                    twitter_stream = twitter.TwitterStream(auth=self._API_TWITTER.auth)
                    if query == '':
                        stream = twitter_stream.statuses.filter(locations=location_api)
                    else:
                        stream = twitter_stream.statuses.filter(track=query, locations=location_api)
                    for tweet in stream:
                        if tweet is not None:
                            # Call food detector service
                            self.food_detector.detect_food(tweet)
                        else:
                            reconnect += 1
                            Logging.write_specific_error("Tweet is None. Reconnect TwitterStreaming #{0}".format(reconnect))
                            self._twitter_api(True)

                            time.sleep(10)
                    break
                except:
                    Logging.write_standard_error(sys.exc_info())
                finally:
                    reconnect += 1
                    Logging.write_specific_error('Trying new connection #{0}'.format(reconnect))
                    time.sleep(10)
                    self._twitter_api(True)
        except:
            Logging.write_standard_error(sys.exc_info())
