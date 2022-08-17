TAG = 1.0.0

.PHONY: all build push

all: build

build:
	python3 setup.py sdist bdist_wheel

publish:
	twine upload dist/cfx-address-${TAG}*

gen-docs:
	cd ./docs && \
	sphinx-apidoc -o ./source ../cfx_address -f -M --separate && \
	make html

test:
	pytest tests
	python3 -m doctest cfx_address/address.py cfx_address/utils.py
