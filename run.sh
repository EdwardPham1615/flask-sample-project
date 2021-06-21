#!/bin/bash
# shellcheck disable=SC2155
export PYTHONPATH=$(pwd)
case ${APP_SERVER:-"gunicorn"} in
    "gunicorn")
        gunicorn -w ${GUNICORN_WORKERS:-"1"} \
                 -b :${GUNICORN_PORT:-"8080"} \
                 -k ${GUNICORN_WORKER_TYPE:-"egg:meinheld#gunicorn_worker"} \
                 --log-level ${GUNICORN_DEBUG:-"DEBUG"} \
                 --capture-output \
                 app:application
        ;;
    "uwsgi")
        # python app.py
        uwsgi --socket 0.0.0.0:${GUNICORN_PORT:-"8080"} \
              --protocol=http \
              -w app:application \
              -b 32768 \
              --workers ${GUNICORN_WORKERS:-"1"}
        ;;
esac
