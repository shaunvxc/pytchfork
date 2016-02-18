#!/usr/bin/env python

from setuptools import setup

install_requires = [
    "redis==2.10.3",
    "multiprocessing_logging",
]

setup(
    name='pytchfork',
    version='0.0.2',
    description='multiprocessing decorator with queue management & redis features',
    author='Shaun Viguerie',
    author_email='shaunvig114@gmail',
    url='https://github.com/shaunvxc/pytchfork',
    install_requires=install_requires,
    license="MIT",
    packages=['pytchfork'],
    zip_safe=True
)
