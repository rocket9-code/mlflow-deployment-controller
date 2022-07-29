ROOT_DIR 	:= $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

lint-python:
	cd ${ROOT_DIR}; python -m mypy
	cd ${ROOT_DIR}; python -m isort feast/ tests/ --check-only
	cd ${ROOT_DIR}; python -m flake8 feast/ tests/
	cd ${ROOT_DIR}; python -m black --check feast tests