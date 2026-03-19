#!/bin/bash

set -e

cd "$(dirname "$0")"

ruff check --ignore=E501,E402,E702,F403 $@ .
