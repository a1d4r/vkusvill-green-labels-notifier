# Vkusvill Green Labels Notifiers

Telegram bot which notifies a user when there are new items with green labels available.

## Table of content

<!-- TOC -->
* [Vkusvill Green Labels Notifiers](#vkusvill-green-labels-notifiers)
  * [Table of content](#table-of-content)
  * [Installation](#installation)
  * [Migrations](#migrations)
  * [Makefile usage](#makefile-usage)
  * [Credits](#credits)
<!-- TOC -->

## Installation

1. Create env file:

```bash
cp envs/.env.example envs/.env
```

2. If you use `pyenv`, create and activate environment.
   You can [read this article](https://fathomtech.io/blog/python-environments-with-pyenv-and-vitualenv/)
   to get familiar with pyenv. Or you can just omit this step, and poetry will install venv for you.

```bash
pyenv install 3.12
pyenv virtualenv 3.12 vkusvill-green-labels
pyenv local vkusvill-green-labels
```

3. If you don't have `Poetry` installed run:

```bash
make poetry-download
```

4. Initialize poetry and install `pre-commit` hooks:

```bash
make install
make pre-commit-install
```

5. Run formatters, linters, and tests. Make sure there is no errors.

```bash
make format lint test
```

6. Run supporting services

```bash
docker compose --profile infra up -d
```

7. Run the application

```bash
make up
```

## Migrations

Create migration:

```bash
alembic revision --autogenerate -m "Message"
```

Review the generated migration file and corresponding SQL:

```bash
alembic upgrade prev_revision_id:revision_id --sql
```

You can find `prev_revision_id` and `revision_id` in the migration file

```
Revision ID: %revision_id%
Revises: %prev_revision_id%
```

Apply migrations:

```bash
alembic upgrade head
```

Revert last migration:

```bash
alembic downgrade -1
```

## Makefile usage

[`Makefile`](https://github.com/a1d4r/vkusvill-green-labels-notifier/blob/master/Makefile) contains a lot of functions
for faster development.

<details>
<summary>1. Download and remove Poetry</summary>
<p>

To download and install Poetry run:

```bash
make poetry-download
```

To uninstall

```bash
make poetry-remove
```

</p>
</details>

<details>
<summary>2. Install all dependencies and pre-commit hooks</summary>
<p>

Install requirements:

```bash
make install
```

Pre-commit hooks could be installed after `git init` via

```bash
make pre-commit-install
```

</p>
</details>

<details>
<summary>3. Codestyle</summary>
<p>

Automatic formatting uses `ruff`.

```bash
make codestyle

# or use synonym
make format
```

Codestyle checks only, without rewriting files:

```bash
make check-codestyle
```

Update all dev libraries to the latest version using one command

```bash
make update-dev-deps
```

</p>
</details>

<details>
<summary>4. Code security</summary>
<p>

This command identifies security issues with `Safety`:

```bash
make check-safety
```

To validate `pyproject.toml` use

```bash
make check-poetry
```

</p>
</details>

<details>
<summary>5. Linting and type checks</summary>
<p>

Run static linting with `ruff` and `mypy`:

```bash
make static-lint
```

</p>
</details>

<details>
<summary>6. Tests with coverage</summary>
<p>

Run tests:

```bash
make test
```

</p>
</details>

<details>
<summary>7. All linters</summary>
<p>

Of course there is a command to ~~rule~~ run all linters in one:

```bash
make lint
```

</p>
</details>

<details>
<summary>8. Docker</summary>
<p>

```bash
make docker-build
```

which is equivalent to:

```bash
make docker-build VERSION=latest
```

Remove docker image with

```bash
make docker-remove
```

More information [about docker](https://github.com/a1d4r/vkusvill-green-labels-notifier/tree/master/docker).

</p>
</details>

<details>
<summary>9. Cleanup</summary>
<p>
Delete pycache files

```bash
make pycache-remove
```

Remove package build

```bash
make build-remove
```

Delete .DS_STORE files

```bash
make dsstore-remove
```

Remove .mypycache

```bash
make mypycache-remove
```

Or to remove all above run:

```bash
make cleanup
```

</p>
</details>

## Credits

Special thanks to [coolitydev](https://github.com/coolitydev) for the help in developing this project.

This project was generated with [`python-package-template`](https://github.com/a1d4r/python-package-template)
