#!/bin/bash
. ~/.adt/venv-adt/bin/activate
echo "Y" | apt install awscli
pip3 install boto3
