#CGSTATS
Models and access to clinstatsdb


## configuration

This module expects a config YAML file to be present in ~/.clinical by the name of `databases.yaml`.

The config file has following form:

```
# connection strings
clinstats:
    connection_string: "mysql://127.0.0.1:3306/db"
    name: 'db'
    version: '2.0.2'
```

The version and name are to be present in the database table `version`.
