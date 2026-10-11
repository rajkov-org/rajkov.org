# rajkov.org — hand-built static site. `make help` lists targets.
# Deploys to prd01 behind the shared `edge` Caddy; see AGENTS.md + deploy/.
.DEFAULT_GOAL := help
.PHONY: help dev check validate edge-push edge-up edge-route edge-verify edge-deploy ftp-list ftp-backup ftp-retire ftp-upload ftp-prune ftp-verify ftp-deploy

EDGE_HOST ?= prd01
EDGE_DIR  ?= /opt/rajkov.org
# Staging by default; production once Cloudflare points rajkov.org at prd01:
#   make edge-verify EDGE_URL=https://rajkov.org
EDGE_URL  ?= https://rajkov.suryasoni.info
PORT      ?= 8086

help:  ## Show this help
	@grep -E '^[a-z-]+:.*?## ' $(MAKEFILE_LIST) | awk -F':.*?## ' '{printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

dev:  ## Serve www/ locally with the SAME origin Caddyfile (http://localhost:$(PORT))
	docker run --rm -it -p $(PORT):80 \
	  -v "$$PWD/www":/srv:ro -v "$$PWD/deploy/Caddyfile":/etc/caddy/Caddyfile:ro \
	  -e XDG_CONFIG_HOME=/tmp -e XDG_DATA_HOME=/tmp caddy:2-alpine

validate:  ## Validate the origin Caddyfile + the edge fragment in a throwaway container
	docker run --rm -v "$$PWD/deploy/Caddyfile":/etc/caddy/Caddyfile:ro \
	  -e XDG_CONFIG_HOME=/tmp -e XDG_DATA_HOME=/tmp caddy:2-alpine caddy validate --config /etc/caddy/Caddyfile
	docker run --rm -v "$$PWD/deploy/caddy/rajkov.caddy":/tmp/frag.caddy:ro \
	  -e XDG_CONFIG_HOME=/tmp -e XDG_DATA_HOME=/tmp caddy:2-alpine \
	  caddy validate --adapter caddyfile --config /tmp/frag.caddy

check: validate  ## Local gate: config validates + every internal link/asset in www/ resolves
	@python3 scripts/check-links.py www

# --inplace is load-bearing: the Caddyfile is bind-mounted as a single file, so
# the mount is pinned to its inode. A temp-file-and-rename rsync creates a new
# inode and the container keeps serving the old config while `up -d` sees
# nothing to do. (Learned on garc-raj.com.)
edge-push: check  ## Ship www/ + config to prd01 (runs the gate first)
	ssh $(EDGE_HOST) 'sudo mkdir -p $(EDGE_DIR) && sudo chown $$(id -u):$$(id -g) $(EDGE_DIR)'
	rsync -az --delete --itemize-changes www/ $(EDGE_HOST):$(EDGE_DIR)/www/
	rsync -az --inplace deploy/Caddyfile deploy/docker-compose.edge.yml $(EDGE_HOST):$(EDGE_DIR)/

edge-up:  ## Create / refresh the origin container on prd01 (validate, then hot-reload)
	ssh $(EDGE_HOST) 'cd $(EDGE_DIR) && docker compose -f docker-compose.edge.yml up -d && \
	  docker exec rajkov-web caddy validate --config /etc/caddy/Caddyfile && \
	  docker exec rajkov-web caddy reload --config /etc/caddy/Caddyfile || true'

edge-route:  ## Ship the edge route fragment and reload the shared edge (atomic)
	rsync -az deploy/caddy/rajkov.caddy $(EDGE_HOST):/tmp/rajkov.caddy
	ssh $(EDGE_HOST) 'sudo cp /tmp/rajkov.caddy /opt/edge/conf.d/rajkov.caddy && \
	  cd /opt/edge && sudo docker compose exec -T caddy caddy reload --config /etc/caddy/Caddyfile'

edge-verify:  ## Smoke-test the live URL (never trust exit 0)
	@bash deploy/verify.sh $(EDGE_URL)

edge-deploy: edge-push edge-up edge-route edge-verify  ## Full deploy: content + container + route + smoke test

# ---- Shared LiteSpeed host (the original rajkov.org hosting) over FTPS.
# Credentials live in ~/.config/rajkov/ftp.env (never in the repo). See deploy/ftp/ftp.py.
BACKUP_DIR ?= $(HOME)/backups/rajkov.org-ftp-$(shell date +%Y%m%d)

ftp-list:  ## Show the FTP account's top-level directory
	@python3 deploy/ftp/ftp.py list

ftp-backup:  ## Mirror the FTP account (or BACKUP_PATHS="public_html wordpress-backups …") to $(BACKUP_DIR) (resumable)
	@python3 deploy/ftp/ftp.py backup "$(BACKUP_DIR)" $(BACKUP_PATHS)

ftp-retire:  ## Move everything in the document root into _retired-wordpress-<date>/ and deny access to it
	@python3 deploy/ftp/ftp.py retire

ftp-upload: check  ## Upload www/ + deploy/htaccess.production (as .htaccess) to the document root
	@python3 deploy/ftp/ftp.py upload

ftp-prune:  ## Delete stray files in the document root that are not in www/
	@python3 deploy/ftp/ftp.py prune

ftp-verify:  ## Smoke-test https://rajkov.org (production rules: indexable)
	@bash deploy/verify.sh https://rajkov.org

ftp-deploy: ftp-upload ftp-verify  ## Upload + smoke test (run ftp-backup and ftp-retire first, once)
