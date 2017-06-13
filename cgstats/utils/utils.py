#!/usr/bin/env python
# encoding: utf-8

from path import Path
from glob import glob

def get_projects(demux_dir, unaligned_dir='Unaligned'):
    """TODO: Docstring for get_projects.

    Args:
        demux_dir (TODO): TODO

    Returns: TODO

    """

    projects = []
 
    project_dirs = glob(Path(demux_dir).joinpath(unaligned_dir, '*'))
    for project_dir in project_dirs:
        project = Path(project_dir).normpath().basename()
        if project.startswith('Project_'):
            project = project.split('_', 1)[1]
            projects.append(project)

    return projects

def gather_flowcell(demux_dir):
    """TODO: Docstring for gather_flowcell.

    Args:
        demux_dir (str): path to demux dir

    Returns: TODO

    """

    rs = {} # result set

    # get the flowcell name
    full_flowcell_name = Path(demux_dir).normpath().basename().split('_')[-1]
    rs['name'] = full_flowcell_name[1:]

    # get the flowcell position: A|B
    rs['pos'] = full_flowcell_name[0]

    return rs
