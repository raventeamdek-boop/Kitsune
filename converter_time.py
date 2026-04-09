<<<<<<< HEAD
from datetime import datetime

def to_datetime_object(date_string, date_format):
    s = datetime.strptime(date_string, date_format)
=======
from datetime import datetime

def to_datetime_object(date_string, date_format):
    s = datetime.strptime(date_string, date_format)
>>>>>>> 4a92891bf11d83a0a39d01b4d6932b7d7751ea52
    return s