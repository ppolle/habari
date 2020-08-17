from dateutil.relativedelta import *
from datetime import datetime, timedelta

def pluralize_date_text(text):
    """ Make date_String plural"""
    split_string = list(text)
    if split_string[-1] is not 's':
        return text+'s'
    else:
        return text

def create_timedelta_object(date_string):
    """ Return Tiimedelta object"""
    parsed_date_String = [date_string.split()[:2]]
    plural_date_string = pluralize_date_text(parsed_date_String[0][1])
    time_digits = float(parsed_date_String[0][0])

    parsed_date_String[0][1] = plural_date_string

    if plural_date_string == 'months':
        dt = relativedelta(months=+time_digits)
    elif plural_date_string == 'years':
        dt = relativedelta(years=+time_digits)
    else:
        time_dict = dict((fmt, float(amount))for amount, fmt in parsed_date_String)
        dt = timedelta(**time_dict)
    
    return datetime.now() - dt