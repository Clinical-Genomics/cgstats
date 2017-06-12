#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cgstats.utils.utils import get_projects, gather_flowcell

def test_get_projects(rapid_run_dir):
    assert sorted(get_projects(rapid_run_dir, 'Unaligned')) == sorted(['454557', '504910', '959191'])

def test_gather_flowcell_rapid(rapid_run_dir):
    assert gather_flowcell(rapid_run_dir) == {'pos': 'A', 'name': 'HB07NADXX'}

def test_gather_flowcell_x(x_run_dir):
    assert gather_flowcell(x_run_dir) == {'pos': 'A', 'name': 'HC7H2ALXX'}
