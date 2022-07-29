ROOT_DIR 	:= $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

lint-python:
	cd ${ROOT_DIR}; python -m isort . --check-only
	cd ${ROOT_DIR}; python -m flake8 mlflow_controller/ 
	cd ${ROOT_DIR}; python -m black --check mlflow_controller 

lint-python-check:
	cd ${ROOT_DIR}; python -m isort mlflow_controller/  --check-only
	cd ${ROOT_DIR}; python -m flake8 mlflow_controller/ 
	cd ${ROOT_DIR}; python -m black --check mlflow_controller 