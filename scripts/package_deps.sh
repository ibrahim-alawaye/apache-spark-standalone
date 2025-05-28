#!/bin/bash
mkdir -p deps
pip install -r api/requirements.txt --target deps/
cd deps && zip -r ../deps.zip . && cd ..