dev:
	cp .env.example .env
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

user:
	# Enter login, email, password and optional --admin flag
	docker-compose exec flask flask create_user $(args)