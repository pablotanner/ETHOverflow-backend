from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'

@app.get('/posts')
def get_posts():
    return ["post1", "post2", "post3"]

@app.post('/posts')
def create_post(data):




if __name__ == '__main__':
    app.run()
