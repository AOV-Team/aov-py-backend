from apps.analytic import dates
from django.test import TestCase
from datetime import datetime
from freezegun import freeze_time


@freeze_time('2017-03-01')
class TestGetMonthDateRanges(TestCase):
    def test_get_month_date_ranges_successful(self):
        """
        Test that we get month date ranges between 2 dates

        :return: None
        """
        ranges = dates.get_month_date_ranges(datetime.now(), datetime(2017, 6, 10))

        self.assertEquals(len(ranges), 4)

        self.assertEquals(ranges[0][0].month, 3)
        self.assertEquals(ranges[0][0].day, 1)
        self.assertEquals(ranges[0][1].month, 3)
        self.assertEquals(ranges[0][1].day, 31)

        self.assertEquals(ranges[3][0].month, 6)
        self.assertEquals(ranges[3][0].day, 1)
        self.assertEquals(ranges[3][1].month, 6)
        self.assertEquals(ranges[3][1].day, 30)

    def test_get_month_date_ranges_reverse(self):
        """
        Test that date order does not matter

        :return: None
        """
        ranges = dates.get_month_date_ranges(datetime(2017, 6, 10), datetime.now())

        self.assertEquals(len(ranges), 4)

        self.assertEquals(ranges[0][0].month, 3)
        self.assertEquals(ranges[0][0].day, 1)
        self.assertEquals(ranges[0][1].month, 3)
        self.assertEquals(ranges[0][1].day, 31)

        self.assertEquals(ranges[3][0].month, 6)
        self.assertEquals(ranges[3][0].day, 1)
        self.assertEquals(ranges[3][1].month, 6)
        self.assertEquals(ranges[3][1].day, 30)

    def test_get_month_date_ranges_same_month(self):
        """
        Test that we get one date range if both dates are in same month

        :return: None
        """
        ranges = dates.get_month_date_ranges(datetime.now(), datetime(2017, 3, 10))

        self.assertEquals(len(ranges), 1)

        self.assertEquals(ranges[0][0].month, 3)
        self.assertEquals(ranges[0][0].day, 1)
        self.assertEquals(ranges[0][1].month, 3)
        self.assertEquals(ranges[0][1].day, 31)

    def test_get_month_date_ranges_diff_year(self):
        """
        Test that we get month date ranges between 2 dates in different years

        :return: None
        """
        ranges = dates.get_month_date_ranges(datetime.now(), datetime(2019, 1, 1))

        self.assertEquals(len(ranges), 23)

        self.assertEquals(ranges[0][0].month, 3)
        self.assertEquals(ranges[0][0].day, 1)
        self.assertEquals(ranges[0][1].month, 3)
        self.assertEquals(ranges[0][1].day, 31)

        self.assertEquals(ranges[22][0].month, 1)
        self.assertEquals(ranges[22][0].day, 1)
        self.assertEquals(ranges[22][1].month, 1)
        self.assertEquals(ranges[22][1].day, 31)


@freeze_time('2017-03-01')
class TestGetNumberOfMonths(TestCase):
    def test_get_number_of_months_successful(self):
        """
        Test that we get the number of months between 2 date ranges

        :return: None
        """
        months = dates.get_number_of_months(datetime.now(), datetime(2017, 6, 10))

        self.assertEquals(months, 3)

    def test_get_number_of_months_next_day_month(self):
        """
        Test that we get 1 month even if next day is next month

        :return: None
        """
        months = dates.get_number_of_months(datetime.now(), datetime(2017, 2, 28))

        self.assertEquals(months, 1)

    def test_get_number_of_months_reverse_order(self):
        """
        Test that order in which dates are provided does not matter

        :return: None
        """
        months = dates.get_number_of_months(datetime(2017, 6, 10), datetime.now())

        self.assertEquals(months, 3)

    def test_get_number_of_months_same_month(self):
        """
        Test that we get 0 if both dates are in same month

        :return: None
        """
        months = dates.get_number_of_months(datetime.now(), datetime(2017, 3, 10))

        self.assertEquals(months, 0)

    def test_get_number_of_months_diff_year(self):
        """
        Test that we can get number of months from different years

        :return: None
        """
        months = dates.get_number_of_months(datetime.now(), datetime(2018, 4, 10))

        self.assertEquals(months, 13)

    def test_get_number_of_months_diff_year_2_years(self):
        """
        Test that we can get number of months from multiple years

        :return: None
        """
        months = dates.get_number_of_months(datetime.now(), datetime(2019, 2, 10))

        self.assertEquals(months, 23)

    def test_get_number_of_months_diff_year_3_years(self):
        """
        Test that we can get number of months from multiple years

        :return: None
        """
        months = dates.get_number_of_months(datetime(2017, 10, 2), datetime(2021, 2, 10))

        self.assertEquals(months, 40)
