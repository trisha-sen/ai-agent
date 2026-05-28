#!/bin/bash
set -e
python load_data.py
exec "$@"
