#! /bin/bash
# This script will install dmr_utils from a downloaded zip file or from a git clone.
# If all you are interested in using dmr_utils because another program requires it (HBlink DMRlink etc)
# Then you can simply:
# apt-get install python3-pip -y
# pip install dmr_utils3

# Install the required support programs
# apt-get install unzip -y
# apt-get install python-dev -y
apt-get install python3-pip -y

test -e ./setup.py || exit 1
pip3 install --upgrade .

