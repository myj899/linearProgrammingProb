from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    # return 'HELLO WORLD'
    return render_template('index.html')