# Deployment: Docker + Git Auto-Pull + GitHub Actions CI/CD

How this app is deployed on the VM: a Django container that keeps itself up to
date via `git pull`, restarted automatically by a GitHub Actions self-hosted
runner on every push to `main`. Cloudflare Tunnel (configured separately,
outside this repo) routes public traffic to the container's published port.

## Architecture

- **App**: Django + DRF, served by gunicorn inside Docker, static files via
  WhiteNoise.
- **Database**: external MySQL server (not bundled in Docker) — configured via
  `DB_HOST`/`DB_PORT`/`DB_NAME`/`DB_USER`/`DB_PASSWORD` in `.env`.
- **Code delivery**: the repo checkout on the VM is bind-mounted into the
  container (`.:/app` in `docker-compose.yml`). The container's entrypoint
  does a fast-forward-only `git pull origin main` on every start, so the
  running code always matches the checkout on disk — no image rebuild needed
  for ordinary app-code changes.
- **CI/CD**: a GitHub Actions workflow (`.github/workflows/deploy.yml`) runs
  on a **self-hosted runner installed on the VM**. On push to `main`, it pulls
  the latest commit and runs `docker compose up -d --build` in place. If the
  VM/runner is offline when you push, GitHub queues the run and it fires the
  moment the runner reconnects — no inbound access to the VM is required,
  since the runner only makes outbound connections to GitHub.
- **TLS/public access**: an existing Cloudflare Tunnel (set up outside this
  repo) points at the container's published port. Nothing in this repo
  manages the tunnel.

## Files involved

| File | Purpose |
|---|---|
| `Dockerfile` | Builds the app image: Python 3.13, TA-Lib C lib, mysqlclient build deps, git, non-root `appuser`. |
| `docker-compose.yml` | Runs the `web` service: bind-mounts the repo, sets the runtime UID/GID, loads `.env`. |
| `docker/entrypoint.sh` | Container entrypoint: git auto-pull → wait for DB → migrate → collectstatic → exec gunicorn. |
| `docker/docker-entrypoint.sh` | Bootstrap script baked outside `/app` (survives the bind mount). Fixes CRLF/exec-bit on `docker/entrypoint.sh` every start (a `git pull`'d file won't carry the build-time fixups), then hands off to it. |
| `.github/workflows/deploy.yml` | The CI/CD workflow: triggers on push to `main` (and manually via `workflow_dispatch`), runs on `runs-on: self-hosted`. |
| `.env` (gitignored, lives only on the VM) | Real secrets/config: DB credentials, `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, `GEMINI_API_KEY`, `OPENROUTER_API_KEY`, etc. Copy from `.env.example` and fill in. |

## One-time VM setup

### 1. Install Docker Engine + Compose plugin (Ubuntu/Debian)

```bash
sudo apt-get remove -y docker.io docker-doc docker-compose podman-docker containerd runc
sudo apt-get update
sudo apt-get install -y ca-certificates curl git
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
sudo usermod -aG docker $USER   # log out/in (or `newgrp docker`) after this
```

Verify: `docker ps` runs with no `sudo` and no permission error; `sudo systemctl is-enabled docker` says `enabled` (so Docker itself survives a VM reboot).

### 2. Clone the repo and configure `.env`

```bash
git clone https://github.com/sandilstha/nepse_techincal_analysis.git
cd nepse_techincal_analysis
cp .env.example .env
nano .env   # fill in real DB_*, DJANGO_*, GEMINI_API_KEY, OPENROUTER_API_KEY, etc.
```

For production, `.env` needs at least:
```
DJANGO_DEBUG=0
DJANGO_SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_urlsafe(64))">
DJANGO_ALLOWED_HOSTS=<every IP/domain this server answers to>
DJANGO_CSRF_TRUSTED_ORIGINS=https://<your-public-domain>
```

### 3. Set the deploy UID/GID

The container writes into the bind-mounted checkout (git pull, collectstatic),
so it needs to run as whichever host user owns the clone:

```bash
id -u   # note this
id -g   # note this
```

Append to `.env`:
```
DEPLOY_UID=<value from id -u>
DEPLOY_GID=<value from id -g>
```

### 4. First build and start

```bash
docker compose up -d --build
docker compose logs -f web
```

Confirm the logs show: git pull, DB connection to your external MySQL,
migrations, collectstatic, then gunicorn listening on `0.0.0.0:8000`.

## CI/CD: GitHub Actions self-hosted runner

**Install the runner in its own directory — NOT inside the app repo.** The
repo directory is bind-mounted into the container and used as the Docker
build context; the runner's binaries (~500MB+) and its private
`.credentials`/`.credentials_rsaparams` key material must not live there.

```bash
mkdir -p ~/actions-runner && cd ~/actions-runner
curl -o actions-runner-linux-x64-<version>.tar.gz -L \
  https://github.com/actions/runner/releases/download/v<version>/actions-runner-linux-x64-<version>.tar.gz
tar xzf ./actions-runner-linux-x64-<version>.tar.gz
```

Get a fresh registration token from GitHub: repo → **Settings → Actions →
Runners → New self-hosted runner** (tokens are single-use and expire after
about an hour), then:

```bash
./config.sh --url https://github.com/sandilstha/nepse_techincal_analysis --token <TOKEN_FROM_GITHUB_UI>
sudo ./svc.sh install
sudo ./svc.sh start
sudo ./svc.sh status   # should show active (running)
```

Installing via `svc.sh` (not `./run.sh`) registers it as a system service that
auto-starts on boot and reconnects to GitHub on its own — this is what makes
"push while the VM is off → it deploys once the VM is back" work.

### Required repo variable

Settings → Secrets and variables → Actions → **Variables** → New repository
variable:
```
Name:  DEPLOY_DIR
Value: /home/<user>/nepse_techincal_analysis
```
This tells the workflow which checkout on the VM to `cd` into and run
`docker compose` from.

### How a deploy runs

`.github/workflows/deploy.yml`, on every push to `main`:
```bash
cd "$DEPLOY_DIR"
git fetch origin main
git merge --ff-only origin/main
docker compose up -d --build
docker compose ps
```
`docker compose up -d --build` is cheap when nothing changed (Docker's layer
cache skips unchanged steps) and guarantees `Dockerfile`/`requirements.txt`
changes are picked up, not just app code.

Manual trigger (no push needed): repo → **Actions** tab → **Deploy** →
**Run workflow**.

## Boot / restart behavior

- `web`'s `restart: unless-stopped` policy means Docker restarts the
  container automatically whenever the Docker daemon (re)starts — covers a
  VM reboot, as long as you didn't manually `docker stop` it beforehand.
- Confirm Docker itself survives a reboot: `sudo systemctl is-enabled docker`
  → `enabled`.
- Confirm the runner survives a reboot: `sudo systemctl is-enabled
  actions.runner.*` (exact unit name includes your repo/runner name — use
  `systemctl list-unit-files | grep actions.runner` to find it).
- **VMware caveat**: all of the above only matters once the VM itself is
  powered on. If the VM is shut down at the hypervisor level, something has
  to start the VM first (manually, or via VMware's own auto-start-on-host-boot
  setting) before anything inside the guest OS can run.

## Troubleshooting notes (things that bit us during setup)

- **`RuntimeError: cannot cache function ... no locator available`** —
  `pandas_ta`'s numba-jitted helpers try to cache next to the (root-owned)
  installed package files; the app runs as a non-root user and can't write
  there. Fixed by setting `NUMBA_CACHE_DIR=/tmp/numba_cache` in the
  `Dockerfile`.
- **`permission denied ... docker.sock`** — the current shell session
  predates your user being added to the `docker` group. Run `newgrp docker`
  or log out/in.
- **Disk fills up fast** on a small VM disk from repeated builds (TA-Lib +
  mysqlclient + numba compile from scratch each time). Reclaim space with:
  ```bash
  docker builder prune -af
  docker image prune -f
  # more aggressive, only if nothing important is unused:
  docker system prune -a --volumes -f
  ```
- **Never extract the Actions runner tarball inside the repo directory** —
  it ends up bind-mounted into the container and included in the Docker
  build context, including its private key material. Always use a separate
  directory (`~/actions-runner`).
