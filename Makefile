.PHONY: up down restart logs shell psql update

up:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose restart odoo

logs:
	docker compose logs -f odoo

shell:
	docker compose exec odoo odoo shell -c /etc/odoo/odoo.conf

psql:
	docker compose exec db psql -U $${POSTGRES_USER:-odoo}

# make update MODULE=erp_customize_base DB=odoo
update:
	docker compose exec odoo odoo -c /etc/odoo/odoo.conf -d $(DB) -u $(MODULE) --stop-after-init
