.PHONY: install-poetry .clean test test-mutation docs-build docs-serve

GIT_SHA = $(shell git rev-parse --short HEAD)
PACKAGE_VERSION = $(shell poetry version -s | cut -d+ -f1)

.install-poetry:
	@echo "---- 👷 Installing build dependencies ----"
	deactivate > /dev/null 2>&1 || true
	pip install -U pip wheel
	poetry -V || pip install -U poetry
	touch .install-poetry

install-poetry: .install-poetry

.init: .install-poetry
	@echo "---- 📦 Building package ----"
	rm -rf .venv
	python -m pip install -U pip wheel
	poetry install --extras migrations
	git init .
	poetry run pre-commit install --install-hooks
	touch .init

.clean:
	rm -rf .init .mypy_cache .pytest_cache .postgres-data
	poetry -V || rm -rf .install-poetry

init: .clean .init
	@echo ---- 🔧 Re-initialized project ----

lint: .init
	@echo ---- ⏳ Running linters ----
	@(poetry run pre-commit run --all-files && echo "---- ✅ Linting passed ----" && exit 0|| echo "---- ❌ Linting failed ----" && exit 1)

postgres-test:
	@(docker kill dev-postgres || true)
	@(docker start test-postgres || docker run --rm -d --name test-postgres --rm -it -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:14 -c fsync=off -c full_page_writes=off -c synchronous_commit=off)
	@(timeout 15s bash -c "until docker exec test-postgres pg_isready ; do sleep 1 ; done")

test: .init postgres-test
	@echo ---- 🧪 Running tests ----
	@(poetry run pytest -v --cov --cov-report term && echo "---- ✅ Tests passed ----" && exit 0 || echo "---- ❌ Tests failed ----" && exit 1)

postgres-dev:
	@(docker kill test-postgres || true)
	@(docker start dev-postgres || docker run --rm --name dev-postgres -p 5432:5432 -e POSTGRES_PASSWORD=postgres -v $(PWD)/.postgres-data:/var/lib/postgresql/data -e PGDATA=/var/lib/postgresql/data/pgdata postgres)
	@(timeout 60s bash -c "until docker exec dev-postgres pg_isready ; do sleep 1 ; done")

run-local: .init postgres-dev
	@echo ---- 🚀 Running app locally ----
	@(poetry run python app/run-local.py)
