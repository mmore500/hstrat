#!/bin/env bash

set -e

cd "$(dirname "$0")/.."

ruff check . --ignore=F403