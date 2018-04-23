# CGSTATS [![Build Status][travis-img]][travis-url]

Models and CRUD to cgstats.

## configuration

cgstats has a parameter `--database` that needs to hold a connection string to the database:

```bash
$ cgstats --database mysql+pymysql://user:pass@127.0.0.1:3306/cgstats
```

## Table description

**supportparams**: holds the data regarding how the demultiplexing was started

**datasource**: holds the data where and when the run was processed

**demux**: holds the basemask and demux datetime

**flowcell**: holds the data about the flowcell and the HiSeq type

**unaligned**: holds the demultiplexing statistics

**sample**: holds the data regarding sample name

**project**: holds the data regarding the project name

**version**: holds the version data of the database itself. Scripts are developed with a certain version of the database in mind and check with each execution if the correct version of the database is being accessed.

**backup**: holds the data regarding backup of a run

**backtape**: holds the backup tape's name

[travis-img]: https://travis-ci.org/Clinical-Genomics/cgstats.svg?branch=master
[travis-url]: https://travis-ci.org/Clinical-Genomics/cgstats
