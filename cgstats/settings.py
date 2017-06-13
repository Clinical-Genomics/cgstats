# -*- coding: utf-8 -*-

import yaml
from os.path import expanduser

class BaseConfig:

    def __init__(self):
        with open(expanduser("~/.clinical/databases.yaml"), 'r') as ymlfile:
            self.config = yaml.load(ymlfile)

    def __getitem__(self, key):
        """Simple array-based getter.

        Args:
            key (str): Gets the value for this key in the YAML file.

        Returns (str, dict): returns the structure underneat this key.

        """
        return self.config[key]
