#!/bin/bash
poetry export -f requirements.txt --output ../deploy/setup/requirements.txt --without=desktop,dev,tests,code_gen,ffmpeg,packaging --with=webui,ujson