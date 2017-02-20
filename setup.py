#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand


# This is a plug-in for setuptools that will invoke py.test
# when you run python setup.py test
class PyTest(TestCommand):

    """Set up the py.test test runner."""

    def finalize_options(self):
        """Set options for the command line."""
        TestCommand.finalize_options(self)
        self.test_args = ['-v']
        self.test_suite = True

    def run_tests(self):
        """Execute the test runner command."""
        # Import here, because outside the required eggs aren't loaded yet
        import pytest
        sys.exit(pytest.main(self.test_args))


with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='clinstatsdb',
    version='0.14.3',
    description='Models and access to clinstatsdb',
    author='Kenny Billiau',
    author_email='kenny.billiau@scilifelab.se',
    packages=find_packages(exclude=('tests*', 'docs', 'examples')),
    include_package_data=True,
    install_requires=required,
    cmdclass=dict(test=PyTest),
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
    platforms='any',
    license='BSD License',
    entry_points={
        'console_scripts': [
            'clinstatsdb = clinstatsdb.cli:root',
        ],
        'clinstatsdb.subcommands.1': [
            'init = clinstatsdb.initialize:init',
            'show = clinstatsdb.db.cli:show',
            'analysis = clinstatsdb.analysis.cli:analysis',
            'sample = clinstatsdb.db.cli:sample',
            'flowcells = clinstatsdb.db.cli:flowcells',
            'samples = clinstatsdb.db.cli:samples',
            'add = clinstatsdb.db.cli:xadd',
            #'delete = clinstatsdb.db.cli:delete',
            'select = clinstatsdb.db.cli:select',
            #'lanestats = clinstatsdb.db.cli:lanestats',
        ],
        'clinstatsdb.models.1': [
            'core = clinstatsdb.db.models',
            'analysis = clinstatsdb.analysis.models',
        ]
    },
)
