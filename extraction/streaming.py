import ast
import configparser
import os
import sys

import food_detection_root
from extraction.twitter_extraction import NetworkAnalysisTwitter
from u_logging.logging import Logging


def run_streaming():
    try:
        Logging.configure_log("StreamingFoodDetector")
        path_to_configuration = food_detection_root.ROOT_DIR + os.path.sep + 'configuration' + os.path.sep \
                                + 'configuration.ini'
        config = configparser.ConfigParser()
        config.read(path_to_configuration)
        access_credentials = {
            "costumer_key": config.get('StreamingAccess', 'customer_key'),
            "customer_secret": config.get('StreamingAccess', 'customer_secret'),
            "oauth_token": config.get('StreamingAccess', 'oauth_token'),
            "oauth_token_secret": config.get('StreamingAccess', 'oauth_token_secret')
        }
        streaming = NetworkAnalysisTwitter(access_credentials)
        locations = ast.literal_eval(config.get('Parameters', 'location'))
        location_coordinates = ''
        for i in range(0, len(locations)):
            location = locations[i]
            if i == len(locations)-1:
                location_coordinates += config.get('Coordinates', location)
            else:
                location_coordinates += config.get('Coordinates', location) + ','
        queries = ast.literal_eval(config.get('Parameters', 'query'))
        query = ''
        for i in range(0, len(queries)):
            aux_query = queries[i]
            if i == len(queries) - 1:
                query += config.get('Queries', aux_query)
            else:
                query += config.get('Queries', aux_query) + ','
        streaming.twitter_streaming(query, location_coordinates)
    except:
        Logging.write_standard_error(sys.exc_info())

run_streaming()
