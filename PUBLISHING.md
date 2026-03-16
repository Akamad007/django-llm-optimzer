# Publishing

This project publishes to PyPI using PyPI Trusted Publishing with GitHub OIDC.

Only the `publish` job in `.github/workflows/python-publish.yml` is granted `id-token: write`. The build job keeps minimal read-only permissions.

## Trigger

Publishing runs from:

- `.github/workflows/python-publish.yml`
- on GitHub Release `published`
- or manually via GitHub Actions `workflow_dispatch`

## PyPI trusted publisher setup

On PyPI, configure a Trusted Publisher that matches this repository exactly:

- GitHub owner: `akamad007`
- Repository: `django-llm-optimizer`
- Workflow file: `.github/workflows/python-publish.yml`
- Environment: `pypi`

The workflow path must match exactly what is configured on PyPI.

## Maintainer notes

- Create a GitHub Release to trigger a publish.
- The publish job uses GitHub OIDC. Do not add `PYPI_TOKEN`, `username`, or `password` secrets.
- Reusable GitHub workflows cannot currently be used as the trusted workflow for PyPI Trusted Publishing.
- If the GitHub environment or workflow path does not match the PyPI Trusted Publisher configuration exactly, publishing will fail.

## Common failure points

- Wrong workflow filename on PyPI, including path mismatches
- Wrong environment name on either GitHub or PyPI
- Stale package name or PyPI URL, such as publishing docs still pointing at an old project
- Trusted Publisher configured for the wrong GitHub repository
