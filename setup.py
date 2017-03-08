#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    # TODO: put package requirements here
    'connexion==1.1.5',
    'sqlalchemy==1.1.6',
    'psycopg2==2.7',
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='connexion_sql_utils',
    version='0.1.0',
    description="Sqlalchemy, Postgres, Connexion utility",
    long_description=readme + '\n\n' + history,
    author="Michael Housh",
    author_email='mhoush@houshhomeenergy.com',
    url='https://github.com/m-housh/connexion_sql_utils',
    packages=[
        'connexion_sql_utils',
    ],
    package_dir={'connexion_sql_utils':
                 'connexion_sql_utils'},
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='connexion_sql_utils',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
