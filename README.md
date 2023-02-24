# Online Cinema API
Sprint 5 in Practicum middle-python course.  
Teamwork of
* [Andrey Lepekhin](https://github.com/andrey-lepekhin)
* [Polina Vasileva](https://github.com/Polinavas95)

## How to run
1. Clone repo
    ```
    git clone https://github.com/andrey-lepekhin/Async_API_sprint_2.git
    cd Async_API_sprint_2
    git restore --source origin/test_data -- tests/functional/testdata/indexes_snapshot.zip
    ```
2. Launch containers  
`make first_run`  will create .env files from examples, build and launch Docker containers.  
After building wait ~1 min for ETL to spin up and fill the database.
  
   FastAPI docs are available at [http://127.0.0.1/api/openapi](http://127.0.0.1/api/openapi)

## Run tests
Full run takes 1 ~min
### In Docker
```
make run_docker_tests_interactive
```

### Locally
* `make run_docker_test_containers` (wait ~20 sec for spin up)
* Use venv or other ways to install tests/requirements.txt
* `pytest .` 

### To stop all docker containers
```
make stop
```

### More commands
```
make run                - start without rewriting env files
make postgresql         - postgresql container console
make elasticsearch      - elasticsearch container console
make etl                - etl container console
make redis              - redis container console
make shows_async        - async-container console
```

## Generate fake data
```
make generate_data
```
Will generate and add 1 mln fake persons, 100 fake genres and 400 000 fake shows. It will take up ~10 minutes and ~1 GB of space.  
Should be run after `make run` or `make first_run` as it uses the etl container to push data.


Have a nice day :)
