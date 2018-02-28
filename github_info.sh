#!/usr/bin/env bash
set -euo pipefail
VIRTUAL_ENV_DISABLE_PROMPT=true
BASEDIR=$(dirname "$0")
pushd ${BASEDIR} > /dev/null
source $(pipenv --venv)/bin/activate
source ${BASEDIR}/.gh-access-token
popd > /dev/null
python ${BASEDIR}/github_info.py

