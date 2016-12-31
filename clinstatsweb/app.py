# -*- coding: utf-8 -*-
from __future__ import division
import os

from flask import Flask, render_template
from flask_alchy import Alchy
from flask_bootstrap import Bootstrap

from clinstatsdb.db import Model
from clinstatsdb.analysis import api as analysis_api

TEMPLATES_AUTO_RELOAD = True
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = os.environ['SQLALCHEMY_DATABASE_URI']
if 'mysql' in SQLALCHEMY_DATABASE_URI:  # pragma: no cover
    SQLALCHEMY_POOL_RECYCLE = 3600

app = Flask(__name__)
app.config.from_object(__name__)
db = Alchy(app, Model=Model)
Bootstrap(app)


@app.template_filter()
def millions(value):
    return "{} M".format(int(value / 1000000))


@app.template_filter()
def percent(value):
    return round(value * 100, 1)


@app.route('/')
def index():
    """Dashboard view."""
    dups = analysis_api.duplicates()
    readsvscov = analysis_api.readsvscov(db)
    return render_template('index.html', dups=dups, readsvscov=readsvscov)


@app.route('/samples')
def samples():
    """Show raw samples data."""
    samples_q = analysis_api.samples().limit(50)
    return render_template('samples.html', samples=samples_q)
