prod:
	cp .env.example .env
	docker-compose -f docker-compose.yml up --build -d
	docker-compose exec api-auth flask db upgrade
user:
	# Enter login, email, password and optional --admin flag
	docker-compose exec api-auth flask create_user $(args)
stop:
	docker-compose -f docker-compose.yml down
generate_data:
	#Generate fake data and push to ES
	docker-compose exec etl-fa python generate_fake_data.py