SHELL := /bin/bash

all: test

clean:
	rm -rf .coverage
	rm -f *.txt~	
	rm -f tests/*.py~
	rm -f pytchfork/*.py~

init:
	python setup.py develop
	pip install -r requirements.txt

install:
	pip install -r requirements.txt

test:
	rm -f .coverage
	nosetests ./tests/
