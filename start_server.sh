#!/bin/bash

export LD_PRELOAD=/usr/lib/libtcmalloc.so

numactl --cpunodebind=0 --membind=0 \
uvicorn app.main:app --host 0.0.0.0 --port 8000
