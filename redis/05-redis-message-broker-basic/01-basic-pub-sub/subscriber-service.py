from redis import Redis
import base64
import json

redis = Redis(decode_responses='utf-8')

if redis.ping() is False:
    raise Exception("Could not connect to redis server")

pubsub = redis.pubsub()
pubsub.subscribe("user_channel")

for record in pubsub.listen():
    if record['type'] == 'message':       
        message = base64.b64decode(record['data']).decode('utf-8')
        message_json = json.loads(message)
        print(f"going to active user {message_json['username']}")
