#!/usr/bin/env python
# encoding: utf-8

from path import Path

def get_samplesheet( demux_dir, file_name='SampleSheet.csv', delim=','):
    """Reads in and parses a samplesheet. The samplesheet is found in the provided demux_dir.
    Lines starting with #, [ and blank will be skipped.
    First line will be taken as the header.

    Args:
        demux_dir (path): FQ path of demux_dir
        delim (str): the samplesheet delimiter

    Returns (list of dicts):
        Keys are the header, values the lines.

    """
    with open(demux_dir + '/' + file_name) as sample_sheet:
        lines = [ line for line in sample_sheet.readlines() if not line.startswith(('#', '[')) and len(line) ] # skip comments and special headers
        lines = [ line.strip().split(delim) for line in lines ] # read lines

        header = lines[0]

        return [ dict(zip(header, line)) for line in lines[1:] ]


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

