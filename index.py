from flask import Flask, request, render_template, jsonify, redirect, url_for
from flask.ext.bootstrap import Bootstrap
from flask.ext.script import Manager
from flask.ext.moment import Moment
from datetime import datetime
import facebook, urllib2, json, MySQLdb, os

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

# utils

def connect_to_db_prod():
''' connection a la db de prod via tunnel ssh'''

	json_conf = open('db.conf')
	confData = json.loads(str(json_conf.read()))
	db = MySQLdb.connect(host=confData['host']['host_enmarche'],
						user=confData['user']['user_enmarche'],
						passwd=confData['pass']['pass_enmarche'],
						db=confData['name']['name_enmarche'])
	return db

@app.route('/today_ad')
def load_stats():
'''stats de la journee en cours'''

	value = 0
	db = connect_to_db_prod()
	cur = db.cursor()
	result = cur.execute("select count(*) from mac_inscriptions where created_at > '2016-04-27 22:00:00' and created_at < '2016-04-28 22:00:00' and adherent = 1;")
	for row in cur.fetchall():
		value = row[0]
		print value
	return jsonify({'today_ad':value})


@app.route('/all_stats')
def load_stats_bis():
''' total marcheurs / adherents'''

	value = 0
	value1 = 0
	db = connect_to_db_prod()
	cur = db.cursor()
	result = cur.execute("select count(*) from mac_inscriptions;")
	for row in cur.fetchall():
			value = row[0]
			print value
	result = cur.execute("select count(*) from mac_inscriptions where adherent = 1;")
	for row in cur.fetchall():
			value1 = row[0]
			print value1
	res = [{'total':value},{'adherents':value1}]
	return jsonify(results=res)

@app.route('/test')
def test():
''' stats de chaque journee depuis le lancement'''

	db = connect_to_db_prod()
	cur = db.cursor()
	x = 5
	stat_list = []
	while x < 29:
		ad = 0
		ma = 0
		start = "16/04/" + str(x) + " 22:00:00"
		end = "16/04/" + str(x + 1) + " 22:00:00"
		request = "select count(*) from mac_inscriptions where created_at > '" + start + "' and created_at < '" + end + "';"
		# print request
		cur.execute(request)
		for row in cur.fetchall():
   			ma = row[0]
   			# print "16/04/" + str(x + 1) + " marcheurs: " + str(ma)
		request1 = "select count(*) from mac_inscriptions where created_at > '" + start + "' and created_at < '" + end + "' and adherent = 1;"
		# print request1
		cur.execute(request1)
		for row in cur.fetchall():
   			ad = row[0]
   			# print "16/04/" + str(x + 1) + " adherents: " + str(ad)
   		print "16/04/" + str(x + 1) + " marcheurs: " + str(ma) + " adherents: " + str(ad) +"."
   		stat_list.append("16/04/" + str(x + 1) + ',' + str(ma) + ',' + str(ad))
		x = x + 1
	return jsonify(results=stat_list)


def update_stats():
''' a virer et utilisation de all_stats'''

	response = urllib2.urlopen('https://www.en-marche.fr/ajax.php?action=stats42')
	try:
		data = json.load(response)
		adherents = data['a']
		marcheurs = data['i']
	except:
		return ('error while fetching data')
	return (marcheurs, adherents)

# route principales

@app.route('/')
def index():
	#db = connect_to_db_prod()
	# load_stats(db)
	data = update_stats()
	adherents = data[1]
	marcheurs = data[0]
	return render_template('index.html', current_time=datetime.utcnow(), ad=adherents, ma=marcheurs)

if __name__ == '__main__':
	manager.run()