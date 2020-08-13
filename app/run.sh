#!/bin/bash
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
/usr/local/bin/streamlit \
        run /root/app/app.py \
        --browser.serverAddress="0.0.0.0" \
        --server.enableCORS=false \
        --server.headless=true \
        --server.port=8080