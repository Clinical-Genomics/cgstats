# -*- coding: utf-8 -*-
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


@app.route('/')
def index():
    """Dashboard view."""
    dups = analysis_api.duplicates()
    return render_template('index.html', dups=dups)
