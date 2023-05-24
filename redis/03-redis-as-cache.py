from flask import Flask
from redis import Redis
import mysql.connector

app = Flask(__name__)
redis = Redis(decode_responses="utf-8")


@app.route("/register/<username>/<firstname>/<lastname>")
def register(username,firstname,lastname):
    mydb = mysql.connector.connect(user='root', 
                                password='root',
                                host='127.0.0.1',
                                database='mysql')
    cursor1 = mydb.cursor()
    q_select = (f"select * from users where username = '{username}'")
    cursor1.execute(q_select)
    user = cursor1.fetchone()
    mydb.commit()
    cursor1.close()
    if user is not None :
        return f"user {username} exists!!"
    
    cursor = mydb.cursor()
    query = (f"insert into users (username, firstname, lastname) values ('{username}','{firstname}','{lastname}')")
    cursor.execute(query)
    mydb.commit()
    cursor.close()
    mydb.close()
    return f"user {username} registered succesfully"

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
