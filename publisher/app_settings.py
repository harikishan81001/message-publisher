from collections import namedtuple

statuses = namedtuple(
    'Status', ['REJ', "QUE", 'SENT', "DLV"]
)

STATUS = statuses(
    REJ='Rejected',
    QUE="Queued",
    SENT="Sent",
    DLV="Delivered",
)
