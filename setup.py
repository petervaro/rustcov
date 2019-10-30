#!/usr/bin/env python3
## INFO ##
## INFO ##

from shutil import copyfile
from distutils.core import setup

copyfile('rustcov.py', 'rustcov')
setup(name='rustcov',
      version='1.0',
      description='Small script to generate and open kcov coverage report',
      author='Peter Varo',
      author_email='hello@petervaro.com',
      url='https://gitlab.com/petervaro/rustcov',
      scripts=['rustcov'],
      install_requires=['toml'])
