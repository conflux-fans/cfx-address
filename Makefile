.PHONY: all build push

all: build

clean:
	rm -rf dist/

build: clean
	python3 setup.py sdist bdist_wheel

publish: 
	twine upload dist/* --repository cfx-address

gen-docs:
	cd ./docs && \
	sphinx-apidoc -o ./source ../cfx_address -f -M --separate && \
	make html

test:
	pytest tests
	python3 -m doctest cfx_address/address.py cfx_address/utils.py
