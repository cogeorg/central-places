#!/usr/bin/env python2.7
"""Source code for website."""

from flask import abort, Flask, render_template, request
from flask.ext.bootstrap import Bootstrap


# Intitialization
app = Flask(__name__)
app.config.from_object(__name__)
app.url_map.strict_slashes = False
bootstrap = Bootstrap(app)


# Controllers
@app.route('/', defaults={'this_site': 'index'})
@app.route('/index', defaults={'this_site': 'index'})
def index(this_site):
    return render_template('index.html', this_site='index')


@app.route('/rankings')
def rankings():
    rtype = request.args.get('rtype', default='comwith')
    rtypes = ['comwith', 'auth']
    time = request.args.get('time', default='late')
    times = ['late', 'early']
    ranking = request.args.get('ranking', default='occurrence')
    rankings = ['occurrence', 'betweenness', 'eigenvector']
    if rtype in rtypes and time in times and ranking in rankings:
        return render_template('rankings.html', rtype=rtype, time=time,
                               ranking=ranking, this_site='rankings')
    else:
        return abort(404)


@app.route('/networks')
def networks():
    net_type = request.args.get('net_type', default='comwith')
    net_types = ['comwith']
    time = request.args.get('time', default='late')
    times = ['late', 'early']
    if net_type in net_types and time in times:
        return render_template('networks.html', net_type=net_type, time=time,
                               this_site='networks')
    else:
        return abort(404)


@app.route('/rings')
def rings():
    focus = request.args.get('focus', default="RENE_M_STULZ").replace("_", " ")
    time = request.args.get('time', default='late')
    times = ['late', 'early']
    if time in times:
        return render_template('rings.html', focus=focus, time=time,
                               this_site='rings')
    else:
        return abort(404)


@app.route('/about')
def about():
    return render_template('about.html', this_site='about')


# Launch for Testing
if __name__ == '__main__':
    app.run(port=8000)
