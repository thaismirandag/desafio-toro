#!/bin/bash
set -e
rm -rf backend/infrastructure/lambda_package/build
mkdir -p backend/infrastructure/lambda_package/build/python

pip install -r backend/infrastructure/lambda_package/requirements.txt -t backend/infrastructure/lambda_package/build/python

cp -r backend/app backend/infrastructure/lambda_package/build/
cp backend/infrastructure/lambda_handler.py backend/infrastructure/lambda_package/build/

cd backend/infrastructure/lambda_package/build

mv python/* .  

zip -r ../../lambda_package.zip .
cd -





