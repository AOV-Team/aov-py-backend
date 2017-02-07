from datetime import datetime
import calendar


def get_number_of_months(date1, date2):
    """
    Get the number of months between 2 dates. Uses abs() so it doesn't matter in which order dates are provided

    :param date1: First date
    :param date2: Second date
    :return: int - number of months
    """
    return abs((date1.year - date2.year) * 12 + date1.month - date2.month)


def get_month_date_ranges(date1, date2):
    """
    Steps though the months between both dates and returns the date range for each month. Dates are returned in
    datetime format:

    [
        (datetime(2017, 3, 1, 0, 0), datetime(2017, 3, 31, 23, 59)),
        (datetime(2017, 4, 1, 0, 0), datetime(2017, 4, 30, 23, 59)),
        (datetime(2017, 5, 1, 0, 0), datetime(2017, 5, 31, 23, 59)),
    ]

    :param date1: First date
    :param date2: Second date
    :return: tuple of date ranges
    """
    date_ranges = list()
    earliest_date = min([date1, date2])
    number_of_months = get_number_of_months(date1, date2)

    counter = 0
    step_month = earliest_date.month
    step_year = earliest_date.year

    while counter <= number_of_months:
        # Reset month and increment year if new year
        if step_month == 13:
            step_month = 1
            step_year += 1

        days_in_month = calendar.monthrange(step_year, step_month)[1]
        first_day = datetime(step_year, step_month, 1)
        last_day = datetime(step_year, step_month, days_in_month, 23, 59, 59)

        date_ranges.append((first_day, last_day,))
        counter += 1
        step_month += 1

    return date_ranges
