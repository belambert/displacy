PROJECT_ID=llm-exp-405305
REGION=us
GAR_REPO="template"
COMMIT=$(shell git rev-parse HEAD)
BASE="us-docker.pkg.dev/$(PROJECT_ID)/$GAR_REPO/main"
VERSION=$(BASE):$(COMMIT)
LATEST=$(BASE):latest


dockerbuild:
	docker build . --file Dockerfile --tag $(LATEST) --platform linux/amd64
	docker tag $(LATEST) $(VERSION)

dockerpush:
	docker push $(LATEST)
	docker push $(VERSION)

check:
	poetry run black --check --color src tests
	poetry run isort --check src tests
	poetry run ruff check .
	poetry run mypy src tests
	poetry run pylint src tests

format:
	poetry run black src tests
	poetry run isort src tests

fix: format
	poetry run ruff . --fix

test:
	poetry run pytest tests
