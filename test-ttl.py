from flask import Flask
from redis import Redis

app = Flask(__name__)
redis = Redis(decode_responses="utf-8")

@app.route("/register/<username>/<firstname>/<lastname>")
def register(username,firstname,lastname):
    redis.hset(f"user:{username}", mapping={"firstname": f"{firstname}", "lastname" : f"{lastname}"})
    return f"user {username} registered"

@app.route("/login/<username>")
def login(username):
    if redis.exists(f"user:{username}"):
        redis.setex("login", "60", username)
        return "login successfully"
    return "user not found!"
    
@app.route("/index")
def index():
    if redis.exists("login"):
        redis.expire("login", "60")
        user_info = redis.hgetall(f"user:{redis.get('login')}")
        return f"Hi , dear {user_info['firstname']} {user_info['lastname']}"
    return "please login first"

if __name__ == "__main__":
    Flask.run(app)
