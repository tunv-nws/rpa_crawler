from dateutil.relativedelta import relativedelta
from datetime import datetime


def get_months_ago(date: datetime, months=1):
    """Get months before date."""
    last_month = date - relativedelta(months=months)
    return last_month


def convert_datetime_to_string(dt: datetime, format="%Y-%m-%d"):
    """Convert datetime to string."""
    if not dt:
        return None
    return dt.strftime(format)


def test(datte):
    pass
