# Created by Samuel Lesuffleur 02-10-2017
#
# Copyright (c) 2017 Sandtable Ltd. All rights reserved.
from setuptools import setup, find_packages


setup(
    name='flask-auth0',
    license='MIT',
    version='0.1.0',
    description='A Flask extension for authenticating web applications using Auth0.',
    author='Samuel Lesuffleur',
    author_email='samuel@sandtable.com',
    url='https://github.com/sandtable/flask-auth0',
    packages=find_packages(),
    platforms='any',
    include_package_data=False,
    install_requires=[
        'flask',
        'authlib',
    ],
    tests_require=[
        'pytest'
    ],
    zip_safe=False,
    keywords='flask auth0 authentication',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Framework :: Flask'
    ]
)
