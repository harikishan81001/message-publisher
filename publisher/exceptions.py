class InvalidMessage(Exception):
    """
    Raised if found invalid message
    """


class AlreadyPendingMessage(Exception):
    """
    Raised in case found message in Queued state
    """


class AlreadyPublished(Exception):
    """
    Raised in case found message delivered
    """
