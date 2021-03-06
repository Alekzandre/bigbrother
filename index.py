from flask import Flask, request, render_template, jsonify, redirect, url_for
from flask.ext.bootstrap import Bootstrap
from flask.ext.script import Manager
from flask.ext.moment import Moment
from datetime import datetime, timedelta
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

	json_conf = open('db.conf')
	confData = json.loads(str(json_conf.read()))
	db = MySQLdb.connect(host=confData['host']['host_enmarche'],
						user=confData['user']['user_enmarche'],
						passwd=confData['pass']['pass_enmarche'],
						port=confData['port']['port_enmarche'],
						db=confData['name']['name_enmarche'])
	return db

@app.route('/today_ad')
def load_stats():

	value = 0
	db = connect_to_db_prod()
	cur = db.cursor()
	base = datetime.utcnow()-timedelta(days=1)
	base = base.strftime("%Y-%m-%d")
	start = str(base) + " 22:00:00"
	request = "select count(*) from mac_inscriptions where created_at > '" + start + "' and created_at < '" + str(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")) + "' and adherent = 1;"
	# print request
	result = cur.execute(request)
	for row in cur.fetchall():
		value = row[0]
	return jsonify({'today_ad':value})


@app.route('/all_stats')
def load_stats_bis():

	value = 0
	value1 = 0
	db = connect_to_db_prod()
	cur = db.cursor()
	result = cur.execute("select count(*) from mac_inscriptions;")
	for row in cur.fetchall():
			value = row[0]
			# print value
	result = cur.execute("select count(*) from mac_inscriptions where adherent = 1;")
	for row in cur.fetchall():
			value1 = row[0]
			# print value1
	res = [{'total':value},{'adherents':value1}]
	return jsonify(results=res)

@app.route('/fundraising_prop')
def stat_amount():

	db = connect_to_db_prod()
	cur = db.cursor()
	request = "select count(distinct(inscrit_id)) from mac_dons where rcode ='00000' and date_don > '2016-05-05 15:00:25' and amount <= 5000;"
	result = cur.execute(request)
	for row in cur.fetchall():
		part = float(row[0])
	request1 = "select count(id) from mac_dons where rcode ='00000' and date_don > '2016-05-05 15:00:25';"
	result1 = cur.execute(request1)
	for row in cur.fetchall():
		value = float(row[0])
	prop = part/value*100
	print part,value, prop
	return jsonify({'prop_50':str(prop)})

@app.route('/today_fund')
def fund_amount_today():

	summ = 0
	db = connect_to_db_prod()
	cur = db.cursor()
	base = datetime.utcnow()-timedelta(days=1)
	base = base.strftime("%Y-%m-%d")
	start = str(base) + " 22:00:00"
	request = "select amount from mac_dons where rcode = '00000' and date_don > '" + start + "' and date_don < '" + str(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")) + "';"
	cur.execute(request)
	for row in cur.fetchall():
   		summ = summ + int(row[0])
   	request1 = "select count(distinct(inscrit_id)) from mac_dons where rcode ='00000' and date_don > '" + start + "' and date_don < '" + str(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")) + "';"
   	cur.execute(request1)
	for row in cur.fetchall():
   		numm = str(row[0])
   	res = [{'amount':str(summ/100)},{'today_num':numm}]
   	return jsonify(results=res)


@app.route('/fundraising')
def fund_amount():

	summ = 0
	db = connect_to_db_prod()
	cur = db.cursor()
	start = "2016-05-05 15:00:25"
	request = "select amount from mac_dons where rcode = '00000' and date_don > '" + start + "';"
	cur.execute(request)
	for row in cur.fetchall():
   		summ = summ + int(row[0])
   	request = "select count(distinct(inscrit_id)) from mac_dons where rcode ='00000' and date_don > '2016-05-05 15:00:25';"
   	cur.execute(request)
	for row in cur.fetchall():
   		numm = str(row[0])
   	res = [{'amount':str(summ/100)},{'donator_num':numm}]
   	return jsonify(results=res)

@app.route('/test')
def test():

	db = connect_to_db_prod()
	cur = db.cursor()
	x = 5
	stat_list = []
	while x < 30:
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
   		# print "16/04/" + str(x + 1) + " marcheurs: " + str(ma) + " adherents: " + str(ad) +"."
   		stat_list.append("16/04/" + str(x + 1) + ',' + str(ma) + ',' + str(ad))
		x = x + 1
	return jsonify(results=stat_list)


# route principales

@app.route('/')
def index():
	marcheurs = '-'
	adherents = '-'
	adherents_today = '-'
	fund = '-'
	fund_num = '-'
	today_fund = '-'
	return render_template('index.html', current_time=datetime.utcnow(), ad=adherents, ma=marcheurs, at=adherents_today, fu=fund, fn=fund_num, tf=today_fund)

if __name__ == '__main__':
	app.run(debug=True,port=5001)