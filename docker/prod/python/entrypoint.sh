#!/bin/sh
python ./relief/manage.py collectstatic --noinput

echo "Running command '$*'"
exec /bin/sh -c "$*"
