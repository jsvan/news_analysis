#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# package setup
#
# ------------------------------------------------

# imports
# -------
import os

# config
# ------
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

# requirements
# ------------
with open('requirements.txt') as f:
    REQUIREMENTS = f.read().strip().split('\n')

if os.path.exists('README.md'):
    long_description = open('README.md').read()
else:
    long_description = ''

#import spacy
#spacy.download('en_core_web_sm')
# exec
# ----
setup(
    name="jsvnews",
    version="0.1.0",
    packages= find_packages(), #['jsvnews'],
    license='',
    author='Julian Vanecek',
    author_email='julian.vanecek@gmail.com',
    url='www.github.com/jsvan',
    install_requires=REQUIREMENTS,
    long_description=long_description,
    long_description_content_type='text/markdown',
    zip_safe=False,
    keywords='',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    scripts=[
            'definitions.py',
            'jsvnews/run.py',
            'jsvnews/src/viz_biz/sentchart_topic.py'
    ],
    test_suite='tests',
)
