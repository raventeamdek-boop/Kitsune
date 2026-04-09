from datetime import datetime

def to_datetime_object(date_string, date_format):
    s = datetime.strptime(date_string, date_format)
    return s