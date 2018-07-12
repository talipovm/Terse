import logging

log = logging.getLogger(__name__)

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

