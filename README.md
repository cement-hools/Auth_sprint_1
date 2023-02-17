


## Run yourself

### Create users
While app is running you can create users like so:
```
make user args="superman super@example.com p@ssword --admin"
```

## Development
### Pre-commit hooks
* pip install pre-commit from requirements.txt
* `pre-commit install`
* Done!

You can run manually via `pre-commit run --all-files` or wait for pre-commit hooks to do it automatically on commit.

### Run dev containers
```
make dev
```