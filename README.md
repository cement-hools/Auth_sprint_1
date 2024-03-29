Repo address:
https://github.com/cement-hools/Auth_sprint_1/

# Flask-based Auth API
Sprint 7 in Practicum middle-python course.  
Teamwork of
* [Maxim Sekachev ](https://github.com/cement-hools)
* [Andrey Lepekhin](https://github.com/andrey-lepekhin)

FastAPI Shows API based on https://github.com/andrey-lepekhin/Async_API_sprint_2

Architecture
[<img src="./schemas/architecture.jpeg" alt="Image of the process architecture" width="400px"/>](./schemas/architecture.jpeg) 

## Run
```
make prod
# That's all, see for yourself:
curl  -H "Content-Type: application/json" -d "{\"login\": \"testuser\", \"email\": \"email@example.com\", \"password\": \"testpassword\"}" http://localhost/api/v1/registration | json_pp -json_opt pretty,canonical
make stop
```

### Migrations
* Apply migrations
```
 flask db upgrade
```
* Auto-generate migration after a model change
```
 flask db migrate -m "message"
```
* Roll back migration
```
 flask db downgrade
```
* Create empty migration
```
 flask db revision -m "message"
```



### Create users
While app is running you can create users like so:
```
make user args="superman super@example.com p@ssword --admin"
```

## Development
### Pre-commit hooks
* `pip install pre-commit`
* `pre-commit install`
* Done!

You can run it manually via `pre-commit run --all-files` or wait for pre-commit hooks to do it automatically on commit.

### Run dev containers
```
make dev
```