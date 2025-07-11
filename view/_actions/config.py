from lib import Logger, Catch
from database import DataBase

logger = Logger("service_django")
catch = Catch(logger)
usedb = DataBase()


# REDIS KEY
USERDATA = "userdata"
USERDATA_COUNT = "count"
