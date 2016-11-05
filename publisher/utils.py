def get_default_policy():
    """
    Default policy for channel
    """
    return '{"maxRetries": 3}'


EXCLUDE_KEYS = []


def get_default_message_format():
    """
    Returns default message schema
    """
    return {
        "payload": {"required": True,},
        "url": {"required": True},
        "headers": {"required": False},
        "method": {"required": False, "default": "POST"},
    }

