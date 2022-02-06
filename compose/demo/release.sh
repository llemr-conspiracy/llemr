#!/bin/bash

# this script is run by heroku before running the new demo

set -o errexit
set -o pipefail
set -o nounset

# TODO: flush db, create superuser, load fixtures, add demo data
python manage.py collectstatic --no-input
python manage.py migrate

