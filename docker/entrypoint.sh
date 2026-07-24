#!/usr/bin/env bash
# Container entrypoint: pull the latest code, wait for MySQL to accept
# connections, apply migrations, gather static files, then hand off to the
# CMD (gunicorn by default).
set -e

cd /app

# ── Auto-deploy: pull latest `main` from the bind-mounted checkout ─────────
# Only fires when /app is a real git working tree (i.e. the repo is
# bind-mounted in via docker-compose, not just COPY'd into the image at build
# time). Fast-forward-only merge: if the server has local commits that
# diverge from origin, this warns and keeps running the current code instead
# of ever discarding history. Set GIT_AUTO_PULL=0 to disable.
if [ "${GIT_AUTO_PULL:-1}" = "1" ] && [ -d .git ]; then
    branch="${GIT_AUTO_PULL_BRANCH:-main}"
    echo "[entrypoint] git: fetching '${branch}' from origin ..."
    if git fetch --quiet origin "${branch}" && git merge --ff-only --quiet "origin/${branch}"; then
        echo "[entrypoint] git: now at $(git rev-parse --short HEAD) ($(git log -1 --format=%s))"
    else
        echo "[entrypoint] WARNING: git auto-pull failed or would not fast-forward — continuing with the code already on disk" >&2
    fi
else
    echo "[entrypoint] git auto-pull disabled or /app is not a git checkout, skipping"
fi

DB_HOST="${DB_HOST:-db}"
DB_PORT="${DB_PORT:-3306}"

echo "[entrypoint] waiting for database at ${DB_HOST}:${DB_PORT} ..."
python - <<'PY'
import os, socket, sys, time

host = os.environ.get("DB_HOST", "db")
port = int(os.environ.get("DB_PORT", "3306"))
for attempt in range(60):
    try:
        with socket.create_connection((host, port), timeout=2):
            print(f"[entrypoint] database is up (after {attempt * 2}s)")
            break
    except OSError:
        time.sleep(2)
else:
    print("[entrypoint] ERROR: database never became reachable", file=sys.stderr)
    sys.exit(1)
PY

echo "[entrypoint] applying database migrations ..."
python manage.py migrate --noinput

echo "[entrypoint] collecting static files ..."
python manage.py collectstatic --noinput

echo "[entrypoint] starting: $*"
exec "$@"
