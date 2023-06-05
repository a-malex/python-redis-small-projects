import sys
from redis import Redis, exceptions as redisExeptions
import docker
from time import sleep
from random import choice

redis = Redis(decode_responses="utf-8")

client = docker.from_env()

container_name = "redis-container"

if client.containers.get(container_name):
    print("container exists")
else :
    try:      
        redis_container = client.containers.run(
            image='redis:latest' ,
            name=f"{container_name}",
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
    
if len(redis.keys("job:*")) == 0:
    # set jobs for test
    redis.hset("job:1", mapping={"stage": "0", "status": "new"})
    redis.hset("job:2", mapping={"stage": "0", "status": "new"})
    redis.hset("job:3", mapping={"stage": "0", "status": "new"})
    redis.hset("job:4", mapping={"stage": "0", "status": "new"})

# worker to get one job and change the values
if len(sys.argv) > 2:
    # get argument values
    sleep_time = int(sys.argv[1])
    worker_number = sys.argv[2]

    while True:
        # get all jobs from Redis and get one job
        jobs = redis.keys("job:*")
        
        if not jobs:
            print(f"No jobs available for worker {worker_number}. Sleeping for {sleep_time} seconds...")
            sleep(sleep_time)
            continue
            
        current_job = choice(jobs)

        # Check for any other worker that fetched this job before or not
        if redis.exists("worker_" + current_job):
            print(f"job conflict {current_job}")
            continue

        # Set worker key to reserve this job for this worker
        redis.set("worker_" + current_job, worker_number)

        while True:
            try:
                sleep(sleep_time)
                
                pipeline = redis.pipeline()

                # use a watch command to monitor the job key for changes
                pipeline.watch(current_job)

                # check if the job has already been completed by another worker
                if redis.hget(current_job, "status") == "done":
                    print(f"Job {current_job} has already been completed.")
                    break

                # get the current values of the job key
                job_values = redis.hgetall(current_job)

                # update the stage and status values in the job key
                job_values["stage"] = "1"
                job_values["status"] = "done"

                # start a transaction using multi
                pipeline.multi()

                # update the job key with the new values
                pipeline.hset(current_job, mapping=job_values)

                # execute the transaction
                pipeline.execute()

                # print a message indicating the job was completed
                print(f"Job {current_job} completed by worker {worker_number}.")
                break

            except redisExeptions.WatchError:
                # another client changed the job key, so we need to retry
                print(f"Transaction failed for worker {worker_number} on job {current_job}. Retrying...")
                continue

        redis.delete("worker_" + current_job)

else:
    print("Insufficient arguments. Please provide sleep time and worker number in arguments. example : x.py 20 1")