from flask import Flask, render_template, session
from flask_cors import CORS

from routes.authenticator import authenticator
from routes.vassistant import vassistant

app = Flask(__name__)
app.secret_key = 'secret_key'
CORS(app)

app.register_blueprint(authenticator)
app.register_blueprint(vassistant)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/adopt')
def adopt():
    return render_template('adopt.html')

@app.route('/news')
def news():
    return render_template('news.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/donate')
def donate():
    return render_template('donate.html')

@app.route('/reportstary')
def reportstary():
    return render_template('reportstary.html')

@app.route('/volunteer')
def volunteer():
    return render_template('volunteer.html')

if __name__ == '__main__':
    app.run(debug=True)
