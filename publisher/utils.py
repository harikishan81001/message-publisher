from django.conf import settings


def get_default_policy():
    """
    Default policy for channel
    """
    return '{"maxRetries": 3}'


EXCLUDE_KEYS = []


def get_backofftime(retries):
    """
    Calculate backoff period
    """
    return (pow(2, retries) * 1000)
