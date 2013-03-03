#!/bin/sh

if [[($1 = "") || ($2 = "")]]; then
    echo "Usage: dev_setip.sh <git user.name> <git user.email>"
    exit 1
fi

#Install git
cd $HOME
wget http://git-core.googlecode.com/files/git-1.8.1.4.tar.gz 
tar xvzf git-1.8.1.4.tar.gz 
cd git-1.8.1.4 
./configure --prefix=$HOME/git 
make 
make install 
export PATH=$PATH:$HOME/git/bin
git config --global user.name=$1
git config --global user.email=$2
ssh-keygen
echo "Copy this key to github. Hit enter after copying"
echo
cat $HOME/.ssh/id_rsa.pub
echo
read
cd $HOmE
git clone git@github.com:mschuma/MicroCloud.git
git status
