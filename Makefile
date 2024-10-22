all: build_package

demo:
	PYTHONPATH=${PWD} python3 example/main.py

build_package:
	python3 -m build
