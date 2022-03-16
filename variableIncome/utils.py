from datetime import datetime
from dateutil.relativedelta import relativedelta

def get_last_year_date():
        n = datetime.now()
        d = relativedelta(years=1)
        n = n - d
        return n.strftime('%d-%m-%Y')