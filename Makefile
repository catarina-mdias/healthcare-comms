
.PHONY: help
help:
	@echo "Commands:"
	@echo "List of CLI operations."
	@echo "venv              : creates development environment."
	@echo "style   	         : runs style formatting."
	@echo "clean             : cleans all unnecessary files."
	@echo "test              : run tests."
	@echo "nb-to-python      : convert notebooks to python."
	@echo "nb-ready          : clean and nb-to-python."


# Environment
.ONESHELL:
venv:
	python3.10 -m venv venv
	source venv/bin/activate && \
	python -m pip install --upgrade pip setuptools wheel pipenv && \
	python -m pipenv install --dev && \
	python -m pip install -e . && \
	pre-commit install && \
	pre-commit autoupdate

# Styling
.PHONY: style
style:
	nbqa black .
	nbqa isort .
	nbqa flake8 .
	black .
	isort .
	flake8 .

# Cleaning
.PHONY: clean
clean: style
	find . -type f -name "*.DS_Store" -ls -delete
	find . | grep -E "(__pycache__|\.pyc|\.pyo)" | xargs rm -rf
	find . | grep -E ".pytest_cache" | xargs rm -rf
	find . | grep -E ".ipynb_checkpoints" | xargs rm -rf
	rm -f .coverage

# Testing
.PHONY: test
test:
	pytest


.PHONY: nb-to-python
nb-to-python:
	jupyter nbconvert notebooks/*.ipynb --to script


.PHONY: nb-ready
nb-ready: clean nb-to-python

.PHONY: launch-app
launch-app:
	uvicorn api.main:app --reload --port 8080 --host 0.0.0.0
