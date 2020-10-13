#! /bin/bash

# Install the required support programs
apt-get install python3 python3-pip python3-dev libffi-dev libssl-dev -y
pip3 install setuptools wheel
pip3 install -r requirements.txt
