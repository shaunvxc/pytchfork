SHELL := /bin/bash

all: test

init:
	python setup.py develop
	pip install -r requirements.txt

install:
	pip install -r requirements.txt

test:
	rm -f .coverage
	nosetests ./tests/
