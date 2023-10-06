# Poetry plugin drop Python upper constraint

With this plugin you can set a python constraints like:

```toml
[tool.poetry.dependencies]
python = ">=3.9,<3.12"
```

And in the exported wheel we will have only `python=">=3.9"`.

The goal is to have an upper constraint to do the lock but to don't have it in the exported wheel,
then to permit to use it with newer Python version.

Config:

```toml
[build-system]
requires = ["poetry-core>=1.0.0", "poetry-plugin-drop-python-upper-constraint>=0.1.0"]
build-backend = "poetry.core.masonry.api"
```

## Contributing

Install the pre-commit hooks:

```bash
pip install pre-commit
pre-commit install --allow-missing-config
```
