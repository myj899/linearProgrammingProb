from flask import Flask, render_template
import os

app = Flask(__name__)

@app.route('/')
def index():
    print("APP IS RUNNING?")
    # return 'HELLO WORLD'
    return render_template('index.html')

@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

if __name__ == "__main__":
    ENVIRONMENT_DEBUG = os.environ.get("DEBUG", False)
    app.run(host='0.0.0.0', port=5000, debug=ENVIRONMENT_DEBUG)