#!/usr/bin/env python
# encoding: utf-8

from path import Path

def get_projects(demux_dir, unaligned_dir='Unaligned'):
    """TODO: Docstring for get_projects.

    Args:
        demux_dir (TODO): TODO

    Returns: TODO

    """

    projects = []

    project_dirs = glob(os.path.join(demux_dir, unaligned_dir, '*'))
    for project_dir in project_dirs:
        projects.append(os.path.basename(os.path.normpath(project_dir)).split('_')[1])

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
