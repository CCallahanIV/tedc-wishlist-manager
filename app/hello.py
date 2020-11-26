from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    return "One small step for a man..."
