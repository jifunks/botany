#!/usr/bin/env bash

set -e

readonly GAME_DIR=${1}
readonly CURRENT_DIR=$(dirname ${0})
readonly PROJECT_ROOT_DIR=${PROJECT_ROOT_DIR:-"${CURRENT_DIR}/.."}

if [ "$#" -ne 1 ]
then
  echo "Usage example: ${0} \"/srv/botany\""
  exit 1
fi

if ! command -v sed &> /dev/null
then
  echo "The script needs the 'sed' program." >&2
  exit 1
fi


mkdir -p "${GAME_DIR}"
chmod 755 "${GAME_DIR}"
echo "The directory '${GAME_DIR}' has been initialized."

sed -i -e \
  "s|GAME_DIR = \".*\"|GAME_DIR = \"${GAME_DIR}\"|g"\
  "${PROJECT_ROOT_DIR}/botany/data_manager.py"

echo "The game directory value has been successfully substitued with '${GAME_DIR}'."
