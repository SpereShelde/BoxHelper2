import configparser

import time
from flask import Flask, render_template, Response, flash, redirect, url_for
import pymysql

from feed import Feed
from torrent_controller import tc

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'
app.debug = True

@app.route('/')
@app.route('/index')
@app.route('/home')
def index():
    return render_template('index.html')

@app.route('/rss')
def users():
    config = configparser.RawConfigParser()
    config.read("config.ini", encoding="utf-8")
    db = pymysql.connect(host=config.get('global', 'host'),
                             port=config.getint('global', 'port'),
                             user=config.get('global', 'user'),
                             passwd=config.get('global', 'passwd'),
                             db=config.get('global', 'db'), charset='utf8')
    cursor = db.cursor()
    cursor.execute('SELECT title, size, promotions, detail_link, download_link, upload_time FROM torrents_collected ORDER BY get_time DESC limit 50')
    results = cursor.fetchall()
    feed = Feed('Box Helper', 'http://127.0.0.1:2020')

    for result in results:
        feed.append_item("%s [%sMB] [%s]" % (result[0], result[1], 'BFreeH' if result[2]==1 else ''), result[3], result[4])
    return Response(feed.get_xml(), mimetype='application/xml')

@app.route('/panel')
def panel():
    return render_template('panel.html')

@app.route('/status', methods=['POST'])
def status():
    if tc.is_alive():
        flash('Box Helper is running.')
    else:
        flash('Box Helper is stopped.')
    return redirect(url_for('panel'))

@app.route('/start', methods=['POST'])
def start():
    if tc.is_alive():
        flash('Box Helper is running.')
    else:
        tc.start()
        time.sleep(2)
        if tc.is_alive():
            flash('Box Helper started.')
        else:
            flash('Box Helper CANNOT start.')
    return redirect(url_for('panel'))

@app.route('/stop', methods=['POST'])
def stop():
    if tc.is_alive():
        tc.stop()
        flash('Box Helper is stopping.')
    else:
        flash('Box Helper already stopped.')
    return redirect(url_for('panel'))

@app.route('/truncate', methods=['POST'])
def truncate():
    if tc.is_alive():
        flash('Box Helper is running. Please stop it first.')
    else:
        config = configparser.RawConfigParser()
        config.read("config.ini", encoding="utf-8")
        db = pymysql.connect(host=config.get('global', 'host'),
                             port=config.getint('global', 'port'),
                             user=config.get('global', 'user'),
                             passwd=config.get('global', 'passwd'),
                             db=config.get('global', 'db'), charset='utf8')
        cursor = db.cursor()
        sql = "DELETE FROM torrents_collected"
        try:
            cursor.execute(sql)
            db.commit()
        except:
            flash('Box Helper CANNOT clear data.')
        cursor.close()
        db.close()
        flash('Box Helper cleared data.')
    return redirect(url_for('panel'))

if __name__ == '__main__':
    app.run(debug=True)