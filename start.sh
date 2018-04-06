#!/bin/bash -eux

FLASK_APP=app.py flask run --port $PORT --host=0.0.0.0
