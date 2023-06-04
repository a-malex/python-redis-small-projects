import sys
from redis import Redis
import docker
from time import sleep

redis = Redis(decode_responses="utf-8")

client = docker.from_env()
try:      
    redis_container = client.containers.run(
        image='redis:latest' ,
        name='redis-container',
        ports={ '6379/tcp': 6379 },
        detach=True
    )
    sleep(20)
except Exception as e:
    print(e)

# Loop until Redis container is ready
while True:
    try:
        # Ping Redis server
        response = redis.ping()

        # If response is PONG, Redis container is ready
        if response == True:
            print("Redis container is ready!")
            break
    except redis.exceptions.ConnectionError:
        pass
    
    # Wait 1 second before trying again
    sleep(1)
    

# set jobs for test

redis.hset("job:1", mapping={"stage": "0", "status": "new"})
redis.hset("job:2", mapping={"stage": "0", "status": "new"})
redis.hset("job:3", mapping={"stage": "0", "status": "new"})
redis.hset("job:4", mapping={"stage": "0", "status": "new"})

# worker to get one job and change the values
if len(sys.argv) > 1 :
    
    # get argument values
    sleep_time = sys.argv[1]
    selected_job = sys.argv[2]
    
    # get all jobs from redis and get one job
    jobs = redis.keys("job:*")
    current_job = jobs[int(selected_job)]
    
    # create pipeline to manage transaction as a worker
    pipeline = redis.pipeline()
    # watch the job to lock it as a transaction 
    pipeline.watch(current_job)
    # changes duration as a transaction
    sleep(sleep_time)
    redis.hset(current_job, mapping={
        "stage": "1",
        "status": "done"
    })
    # finaly execute pipeline to apply changes on job a transactional act 
    pipeline.execute()
    
else :
    print("insert sleep_time in seconds and job number from 0 to 3 as arg value like : x.py 20 1 ")
