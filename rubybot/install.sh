#!/bin/bash

# Install Dependencies
pip3 install async
pip3 install discord.py
pip3 install tweepy
pip3 install bs4

# Install Opus Dependency
# http://www.linuxfromscratch.org/blfs/view/svn/multimedia/opus.html

wget http://downloads.xiph.org/releases/opus/opus-1.1.3.tar.gz
tar zxfv opus-1.1.3.tar.gz
cd opus-1.1.3
./configure --prefix=/usr --disable-static --docdir=/usr/share/doc/opus-1.1.3
make
make install