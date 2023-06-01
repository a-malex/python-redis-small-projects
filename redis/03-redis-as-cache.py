from flask import Flask
from redis import Redis
import mysql.connector
import docker

print('Hi')

client = docker.from_env()

try:
    mysql_container = client.containers.run(
        image='mysql:latest',
        name='mysql-container',
        ports={'3306/tcp': 3306},
        environment={
            'MYSQL_ROOT_PASSWORD': 'password',
            'MYSQL_DATABASE': 'my_database'
        },
        detach=True
    )

    # Check that the database is available
    result = mysql_container.exec_run('mysql --user=root --password=password -e "SELECT * FROM my_database;"')
    if result.exit_code != 0:
        raise Exception('Failed to connect to the MySQL container')
    print('MySQL container is running and the database is available')
except Exception as e:
    print(e)

try:      
    redis_container = client.containers.run(
        image='redis:latest' ,
        name='redis-container',
        ports={ '6379/tcp': 6379 },
        detach=True
    )
    redis = Redis(decode_responses="utf-8")
    
except Exception as e:
    print(e)
    

app = Flask(__name__)


def db_connect():
    # Create a connection to the database
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="my_database"
    )
    
    return mydb

@app.route('/inital-db')
def initialDb():
    
    mydb = db_connect()
    
    # Create a cursor object to execute SQL queries
    cursor = mydb.cursor()

    # Define the SQL query to create a new table with columns
    sql_query = "CREATE TABLE users (id INT AUTO_INCREMENT PRIMARY KEY, firstname VARCHAR(255), lastname VARCHAR(255) , username VARCHAR(255))"

    # Execute the query to create the table
    result = cursor.execute(sql_query)
    
    if result:
        raise Exception('Failed to create table')
    print('Table users created')
    
    # Commit the changes to the database
    mydb.commit()

    # Close the database connection
    mydb.close()
    
    return 'table users created'

@app.route("/register/<username>/<firstname>/<lastname>")
def register(username,firstname,lastname):
    
    if redis.exists(f"user:{username}") :
        return f"user {username} exists!!"
    
    mydb = db_connect()    
    
    cursor = mydb.cursor()
    query = (f"insert into users (username, firstname, lastname) values ('{username}','{firstname}','{lastname}')")
    cursor.execute(query)
    mydb.commit()
    cursor.close()
    mydb.close()
    redis.hset(f"user:{username}", mapping={"firstname": f"{firstname}", "lastname" : f"{lastname}"})
    return f"user {username} registered succesfully"

@app.route("/login/<username>")
def login(username):
    if redis.exists(f"user_login:{username}") :
        user_redis = redis.hgetall(f"user:{username}")
        return f"welcome MR {user_redis['firstname']} {user_redis['lastname']}"
    mydb = db_connect()
    cursor = mydb.cursor()
    user_query = (f"select * from users where username = '{username}'")
    cursor.execute(user_query)
    user = cursor.fetchone()
    if user is not None:
        redis.hset(f"user:{username}", mapping={"id": user[0], "firstname": user[1], "lastname": user[2], "username": user[3]})
        redis.setex(f"user_login:{username}", "60", "yes")
        return f"welcome MR {user[1]} {user[2]}"
    return "please register first"
    

if __name__ == "__main__":
    Flask.run(app)
