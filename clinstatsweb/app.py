# -*- coding: utf-8 -*-
from __future__ import division
import os

from flask import Flask, render_template
from flask_alchy import Alchy
from flask_bootstrap import Bootstrap

from cgstats.db import Model
from cgstats.analysis import api as analysis_api
from cgstats.analysis.models import AnalysisSample

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
    most_dups = (AnalysisSample.query.order_by(AnalysisSample.duplicates_percent.desc())
                               .limit(5))
    least_mapped = (AnalysisSample.query.filter(AnalysisSample.mapped_percent != None)
                                  .order_by(AnalysisSample.mapped_percent)
                                  .limit(5))
    order_attr = AnalysisSample.completeness_target_10
    filter_cond = AnalysisSample.completeness_target_10 != None
    least_complete = (AnalysisSample.query.filter(filter_cond)
                                    .order_by(order_attr).limit(5))
    dups = analysis_api.duplicates()
    readsvscov = analysis_api.readsvscov(db)
    return render_template('index.html', dups=dups, readsvscov=readsvscov,
                           most_dups=most_dups, least_mapped=least_mapped,
                           least_complete=least_complete)


@app.route('/samples')
def samples():
    """Show raw samples data."""
    samples_q = analysis_api.samples().limit(50)
    return render_template('samples.html', samples=samples_q)


@app.route('/report')
def report():
    """Show qc report."""
    samples_q = analysis_api.samples().limit(5)
    return render_template('report.html', samples=samples_q)
