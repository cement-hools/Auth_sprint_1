prod:
	cp .env.example .env
	docker-compose -f docker-compose.base.yml -f docker-compose.prod.yml up --build -d
dev:
	docker-compose -f docker-compose.base.yml -f docker-compose.dev.yml up --build
user:
	# Enter login, email, password and optional --admin flag
	docker-compose exec flask flask create_user $(args)
stop:
	docker-compose -f docker-compose.base.yml -f docker-compose.prod.yml down