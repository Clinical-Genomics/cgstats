# -*- coding: utf-8 -*-

import yaml
from os.path import expanduser

class BaseConfig:

    def __init__(self):
        with open(expanduser("~/.clinical/databases.yaml"), 'r') as ymlfile:
            self.get = yaml.load(ymlfile)
