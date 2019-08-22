#!/bin/bash

# Install Dependencies
python3 -m pip install -U discord.py
python3 -m pip install -U async
python3 -m pip install -U discord.py
python3 -m pip install -U tweepy
python3 -m pip install -U bs4
python3 -m pip install -U seiutils

# Install Opus Dependency
# http://www.linuxfromscratch.org/blfs/view/svn/multimedia/opus.html

wget http://downloads.xiph.org/releases/opus/opus-1.1.3.tar.gz
tar zxfv opus-1.1.3.tar.gz
cd opus-1.1.3
./configure --prefix=/usr --disable-static --docdir=/usr/share/doc/opus-1.1.3
make
make install