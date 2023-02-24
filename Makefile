run:
	#Команда для первого запуска
	cp .env.example .env
	cp .docker.env.example .docker.env
	cp .docker.env.example tests/.docker.env
	docker-compose -f docker-compose.yml -f docker-compose.etl.yml up --build -d

generate_data:
	#Generate fake data and push to ES
	docker-compose exec etl python etl/postgres_to_es/generate_fake_data.py

stop:
	#Остановка и удаление контейнеров, запущенных docker-compose up.
	docker-compose down

run_docker_tests_interactive:
	# Build and spin up main services, and run all tests interactively
	unzip -o ./tests/functional/testdata/indexes_snapshot.zip -d ./tests/functional/testdata/
	docker-compose -f docker-compose.yml -f tests/docker-compose.yml -f tests/docker-compose.tests.yml up --build

run_docker_test_containers:
	# Build and spin up main services with open external ports.
	# Use when you want to run tests locally of debug services directly
	unzip -o ./tests/functional/testdata/indexes_snapshot.zip -d ./tests/functional/testdata/
	docker-compose -f docker-compose.yml -f tests/docker-compose.yml up --build -d