#! -*- coding: utf-8 -*-
from setuptools import setup, find_packages


setup(name='soundfile',
      version='0.0.1',
      author='Kang Hyojun',
      author_email='admire9@gmail.com',
      packages=find_packages(),
      install_requires=[
          'pytest==2.6.0', 'sphinx'
      ])
