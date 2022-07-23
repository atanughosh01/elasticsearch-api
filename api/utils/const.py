""" Module containing the necessary constants """

# host and port
APP_HOST = "127.0.0.1"
APP_PORT = 5000

# this much records will be fetched to restrain server-load
RECORDS = 20

# only this much indices can be created
MAX_IDX_LIM = 10

# es connection retry is aborted after this number of retries
ES_CONNECT_MAX_RETRIES = 10

# in seconds, es connection retry timesout after this much time
ES_CONNECT_TIMEOUT = 30

# in s, operations on cluster timesout after this much of time
# REQUEST_TIMEOUT = 0.0001
REQUEST_TIMEOUT = 1

# should not contain in names
SPECIAL_CHARS = r"[@!#$%^&*()<>?/\|}{~:]"

# indices should start with this prefix
INDEX_NAME_PREFIX = "sample_"
