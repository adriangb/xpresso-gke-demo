# RealWorld example app

This app is a [RealWorld] example app made using [Xpresso].

## Quick Start

From the root directory of the repo, run:

```shell
make init && make test
```

You need to have Python 3.10 configured as your default python version to run this.
If you don't have Python 3.10 installed, you can install it using [Pyenv].

This will set up a virtual environment (called `.venv`) in the root of the repo, install all of the project dependencies and then run the tests.
Tests require Postgres, which will be started up as a persistent docker container.

### Testing

Run:

```shell
make test
```

### Linting

Linting will auto-run on each commit.
To disable this for a single commit, run:

```shell
git commit -m "<commit message>" --no-verify
```

To disable this permanently:

```shell
poetry run pre-commit --uninstall
```

To run linting manually (without committing):

```shell
make lint
```

### Versioning

So that we can include info about the project version in our infra (in particular, we want the version in the image tag) we keep the source of truth in a `VERSION.txt` file at the root of the repo.
This is also convenient to programmatically check for version bumps (for example in CI).

This version is synced to the Python package version (in `pyproject.toml`) via a pre-commit hook.

### Dependency specification

Dependencies are specified in `pyproject.toml` and managed by Poetry.
But we don't want to have to install Poetry to build the image, so we export Poetry's lockfile to a `app/requirements.txt` via a pre-commit hook.
Then when we build the image we can just `pip install -r app/requirements.txt`.

[RealWorld]: https://realworld-docs.netlify.app
[Xpresso]: https://xpresso-api.dev/
[Pyenv]: https://github.com/pyenv/pyenv
[Poetry]: https://python-poetry.org
