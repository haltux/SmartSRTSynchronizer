__author__ = 'haltux'

#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import smartSRTSynchronizer

from setuptools import setup,find_packages

README = ''
try:
    f = open('README.txt')
    README = f.read()
    f.close()
except:
    pass

REQUIRES = []
if sys.version_info < (2, 6):
    REQUIRES.append('chardet')
else:
    REQUIRES.append('charade')

if sys.version_info < (2, 7):
    REQUIRES.append('argparse')

REQUIRES.append("pysrt")
REQUIRES.append("distribute")

setup(name='smartSRTSynchronizer',
      version=smartSRTSynchronizer.VERSION_STRING,
      author='haltux',
      author_email='haltux2@gmail.com',
      packages = find_packages(),
      package_data={'smartSRTSynchronizer': ['data/en-fr-wikt.txt']},
      entry_points={'console_scripts': ['smartSRTSynchronizer = smartSRTSynchronizer.smartSRTSynchronizer:main']},
      description = "Automatic Subtitle Synchronizer",
      long_description=README,
      license="GPLv3",
      platforms=["Independent"],
      keywords="SubRip srt subtitle synchronization",
      url="https://github.com/haltux/SmartSRTSynchronizer",
      classifiers=[
          "Development Status :: 4 - Beta",
          "Intended Audience :: End Users/Desktop",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Topic :: Multimedia :: Video",
      ]
)