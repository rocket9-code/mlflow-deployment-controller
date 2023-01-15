ROOT_DIR 	:= $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

lint-python:
	cd ${ROOT_DIR}; python -m isort . --recursive --atomic 
	cd ${ROOT_DIR}; python -m black  .
	cd ${ROOT_DIR}; python -m flake8 mlflow_controller/ 
	cd ${ROOT_DIR}; python -m flake8 ui/ 
	# autoflake --remove-all-unused-imports -i -r .


lint-python-check:
	# cd ${ROOT_DIR}; python -m isort mlflow_controller/  --check-only
	cd ${ROOT_DIR}; python -m flake8 mlflow_controller/ 
	cd ${ROOT_DIR}; python -m black --check mlflow_controller 
	cd ${ROOT_DIR}; python -m black --check ui