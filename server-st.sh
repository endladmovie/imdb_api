#!/bin/bash
python /root/lite_api/server.py
python3 -m http.server 3337 --directory /root/lite_api/
