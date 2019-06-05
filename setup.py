# -*- coding: utf-8 -*-

from codecs import open

from setuptools import find_packages, setup

with open('README') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='divebomb',
<<<<<<< HEAD
    version='1.0.8',
=======
    version='1.1.0',
>>>>>>> Added modified functions for profiling, clustering, and exporting
    description='divebomb dive classification algorithm',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Alex Nunes',
    include_package_data=True,
    author_email='alex.et.nunes@gmail.com',
    url='https://github.com/alexetnunes/divebomb',
    download_url='https://github.com/alexetnunes/divebomb',
    license='GPLv2',
    packages=find_packages(exclude=('tests', 'docs'))
)
