""" Module containing the necessary constants """

APP_HOST = "127.0.0.1"

APP_PORT = 5000

RECORDS = 100

# Only this much indices can be created
MAX_ACCESSABLE_IDX_LIM = 10

# In seconds, es connection retry timesout after this much time
ES_CONNECT_TIMEOUT = 30

# es connection retry is aborted after this number of retries
ES_CONNECT_MAX_RETRIES = 10

# In ms, operations on cluster timesout after this much of time
REQUEST_TIMEOUT = 1

SPECIAL_CHARS = r"[@!#$%^&*()<>?/\|}{~:]"

INDEX_NAME_PREFIX = "tdp_interns_"


# ------------------------------------------------------------------------------------------------ #

# import random

# EMPLOYEES = ["Atanu Ghosh", "Abhi Das", "Rajib Roy", "Sudipto Mondal", "Akash Pal", "Anupam Dey"]

# DEPTS = ['SWE-I', 'DevOps Engineer', 'SWE-II', 'IT Support', 'Tester', 'DB Admin']

# L_LIM = 8_00_000_0000

# R_LIM = 9_99_999_9999

# NUM_LIST = random.sample(range(100, 999), len(EMPLOYEES))

# EMP_IDS = random.sample(range(L_LIM % 100000, R_LIM % 100000), len(EMPLOYEES))

# PHN_NOS = random.sample(range(L_LIM, R_LIM), len(EMPLOYEES))

# EMAIL_IDS = []

# idx = 0
# for emp in EMPLOYEES:
#     lst = emp.lower().split(' ')
#     f_name, l_name = lst[0], lst[-1]
#     email_id = f_name + '_' + l_name + '_' + str(NUM_LIST[idx]) + '@uhg.com'
#     EMAIL_IDS.append(email_id)
#     idx += 1
