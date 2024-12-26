up:
	docker compose up --build

cleanup:
	docker compose down
	docker volume rm get-vpn-bot_db_data
	docker compose up --build