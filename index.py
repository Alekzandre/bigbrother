from flask import Flask, request, render_template
from flask.ext.bootstrap import Bootstrap
from flask.ext.script import Manager
from flask.ext.moment import Moment
from datetime import datetime
import facebook, urllib2, json

app = Flask(__name__)
manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)

# gestion des pages d'erreurs

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404

@app.errorhandler(500)
def page_not_found(e):
	return render_template('500.html'), 500

# routes principales

def update_stats():
	response = urllib2.urlopen('https://www.en-marche.fr/ajax.php?action=stats42')
	try:
		data = json.load(response)
		adherents = data['a']
		marcheurs = data['i']
	except:
		return ('error while fetching data')
	return (marcheurs, adherents)

@app.route('/')
def index():
	try:
		data = update_stats()
		adherents = data[1]
		marcheurs = data[0]
	except:
		return render_template('index.html', current_time=datetime.utcnow())
	return render_template('index.html', current_time=datetime.utcnow(), ad=adherents, ma=marcheurs)

if __name__ == '__main__':
	manager.run()
