#!/usr/bin/env bash

export NONINTERACTIVE=1
export DEBIAN_FRONTEND=noninteractive

#
# Packages
#
apt-get update

# https://stackoverflow.com/questions/55313610/importerror-libgl-so-1-cannot-open-shared-object-file-no-such-file-or-directo
# https://askubuntu.com/questions/1060903/importerror-libgthread-2-0-so-0-cannot-open-shared-object-file-no-such-file-o
apt-get install -y \
  libgl1 \
  libglib2.0-0

#
# Python UV
#
export UV_INSTALL_DIR="/usr/local/bin"
curl -LsSf https://astral.sh/uv/0.6.14/install.sh | sh

#
# Permissions
#
chown -R 1000:1000 /home/ubuntu/.cache
