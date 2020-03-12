# -*- coding: utf-8 -*-

# Learn more: https://github.com/iandorsey00/geodata

from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='geodata',
    version='0.1.0a',
    description='A program for getting information about and comparing geographies',
    long_description=readme,
    author='Ian Dorsey',
    author_email='ian.dorsey@gmail.com',
    url='https://github.com/iandorsey00/geodata',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)