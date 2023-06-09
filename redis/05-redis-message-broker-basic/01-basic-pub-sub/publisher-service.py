from redis import Redis
import json
import base64

redis = Redis(decode_responses='utf-8')

if redis.ping() is False:
    raise Exception("Could not connect to redis server")

user = {
    "username": "malex",
    "email": "ahmad@malex.com"
}

message = json.dumps(user).encode('ascii')
message = base64.b64encode(message)

redis.publish("user_channel", message)