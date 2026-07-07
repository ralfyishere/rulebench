#!/bin/sh
# nightly keepalive ping
python3 -c "from client import old_fetch; print(old_fetch('/ping'))"
