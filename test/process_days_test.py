import calendar
from u_generic.utils import Utils

years = [2017]
int_months = [9]
# Process each month from each year
for year in years:
    month_index = 0
    for month in int_months:
        dates = Utils().get_query_dates_per_year_and_month(year, month)
        start_date = dates[0]
        # print(start_date)
        finish_date = dates[1]
        # print(finish_date)
        days = calendar.monthrange(year, month)[1]
        days_times = 1
        month_times = int(days/days_times)
        start_days_count = 1
        end_days_count = 1
        print(month_times)
        print(days)
        for aux_days in range(0, month_times):
            start_days_count = end_days_count
            start_date = start_date.replace(day=start_days_count)
            print(start_date)
            end_days_count += days_times
            print(end_days_count)
            print(days)
            if end_days_count <= days:
                conversations_finish_date = start_date.replace(day=end_days_count)
            else:
                conversations_finish_date = finish_date
            print(conversations_finish_date)
            for i in range(0, 23):
                hour_start_date = start_date.replace(hour=i)
                print(hour_start_date)
                hour_end_date = start_date.replace(hour=i+1)
                print(hour_end_date)
            hour_start_date = start_date.replace(hour=i+1)
            print(hour_start_date)
            hour_end_date = conversations_finish_date
            print(hour_end_date)
            print()

