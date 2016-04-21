from flask import Flask, request, render_template
from flask.ext.bootstrap import Bootstrap
from flask.ext.script import Manager
from flask.ext.moment import Moment
from datetime import datetime

app = Flask(__name__)
manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404

@app.errorhandler(500)
def page_not_found(e):
	return render_template('500.html'),500

@app.route('/')
def index():
	user_agent = request.headers.get('User-Agent')
	return render_template('index.html', ue=user_agent, current_time=datetime.utcnow())

if __name__ == '__main__':
	manager.run()