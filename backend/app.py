from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>Railway Deployed!</h1><p>Auto-deployed from GitHub!</p>'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
