class InvalidMessage(Exception):
    """
    Raised if found invalid message
    """


class AlreadyPendingMessage(Exception):
    """
    Raised in case found message in Queued state
    """
