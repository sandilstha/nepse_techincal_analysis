#!/usr/bin/env bash
# Bootstrap that lives outside /app, so it isn't shadowed when the repo is
# bind-mounted over /app for the git-auto-pull deploy flow. A `git pull` can
# bring in a fresh checkout of docker/entrypoint.sh that lost its exec bit or
# carries CRLF line endings (repo is authored on Windows) — fix both on every
# start before handing off to it.
set -e

sed -i 's/\r$//' /app/docker/entrypoint.sh
chmod +x /app/docker/entrypoint.sh

exec /app/docker/entrypoint.sh "$@"
