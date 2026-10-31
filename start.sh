#!/bin/sh
cd "$(dirname "$0")"
(cd cb && python3 -m catchblock.cli serve) &
cd web && npm install && npm run dev
