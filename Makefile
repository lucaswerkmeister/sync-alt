.PHONY: all check fix

all: requirements.txt dev-requirements.txt check

check:
	black --check .
	ruff check
	mypy

fix:
	black .
	ruff check --fix

requirements.txt: pyproject.toml
	pip-compile --output-file=$@ $^

dev-requirements.txt: pyproject.toml
	pip-compile --extra=dev --output-file=$@ $^
