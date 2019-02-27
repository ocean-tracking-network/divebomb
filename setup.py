# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from codecs import open

with open('README') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='divebomb',
    version='1.0.3',
    description='divebomb dive classification algorithm',
    long_description=readme,
    author='Alex Nunes',
    include_package_data=True,
    author_email='anunes@dal.ca',
    url='https://gitlab.oceantrack.org/anunes/divebomb',
    download_url = 'https://gitlab.oceantrack.org/anunes/divebomb',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
