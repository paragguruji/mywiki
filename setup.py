# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='mywiki',
    version='0.0.1',
    description='Experiments for structured data extraction from unstructured \
        data using Wikipedia corpus',
    long_description=readme,
    author='Parag Guruji',
    author_email='pguruji@purdue.edu',
    url='https://github.com/paragguruji/mywiki',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
