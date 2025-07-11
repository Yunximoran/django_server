from lib import Logger, Catch

logger = Logger("service_django")
catch = Catch(logger)


# REDIS KEY
USERDATA = "userdata"
USERDATA_COUNT = "count"
