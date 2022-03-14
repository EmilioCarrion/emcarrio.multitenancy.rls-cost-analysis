.PHONY: clean-pyc clean-build release docs help
.PHONY: lint test coverage test-codecov
.DEFAULT_GOAL := help

help:
	@grep '^[a-zA-Z]' $(MAKEFILE_LIST) | sort | awk -F ':.*?## ' 'NF==2 {printf "\033[36m  %-25s\033[0m %s\n", $$1, $$2}'

run: 
	docker-compose run python python main.py

run-metrics: 
	docker-compose run python python metrics.py

build: 
	docker-compose build

install-requirements:
	pip install -r requirements.txt

