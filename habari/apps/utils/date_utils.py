import re
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
    short_string_format = re.search(r"(\d+h?m?s?,? )?ago" ,date_string)

    if short_string_format:
        time_string = date_string.split()[0]
        time_amnt = re.findall(r'\d+', time_string)[0]
        time_format = re.findall(r'[a-zA-Z]', time_string)[0]

        if time_format == 'h':
            update_fmt = 'hours'
        elif time_format == 'm':
            update_fmt = 'minutes'
        elif time_format == 's':
            update_fmt = 'seconds'
        elif time_format == 'd':
            update_fmt = 'days'
        elif time_format == 'w':
            update_fmt = 'weeks'
        else:
            update_fmt = 'milliseconds'

        dt = timedelta(**{update_fmt:float(time_amnt)})
    else:
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