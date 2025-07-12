from lib import Logger, Catch
# from channels.generic.websocket import WebsocketConsumer
from channels.generic.websocket import WebsocketConsumer




logger = Logger("service_django")
catch = Catch(logger)


# REDIS KEY
USERDATA = "userdata"
USERDATA_COUNT = "count"
