# Contributing

Thanks.

## Setup

You need Python 3.8 or newer. There is nothing to install.

```bash
python scripts/build.py --serve
python -m unittest discover -s tests
```

## Guidelines

- Keep the build dependency-free (standard library only) and the site framework-free.
- Follow the conventions in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md): numbered CSS and JavaScript files, `component-part` class names, `is-` state classes.
- Do not commit personal data, secrets or `.env` files. Example content must stay generic.
- Add or update a test for any change to the build tool.
- Check both themes and a narrow (mobile) viewport for visual changes.

## Pull requests

1. Fork the repository and create a branch from `main`.
2. Make your change and run the tests.
3. Describe what changed and why, with screenshots for visual changes.
