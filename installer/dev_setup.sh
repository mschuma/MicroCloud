#!/bin/sh

#Install git
cd $HOME
wget http://git-core.googlecode.com/files/git-1.8.1.4.tar.gz 
tar xvzf git-1.8.1.4.tar.gz 
cd git-1.8.1.4 
./configure --prefix=$HOME/git 
make 
make install 
export PATH=$PATH:$HOME/git/bin
git config --global user.name="Devendra D. Chavan"
git config --global user.email="ddchavan@ncsu.edu"
ssh-keygen
echo "Copy this key to bitbucket/github. Hit enter after copying"
echo
cat $HOME/.ssh/id_rsa.pub
echo
read
cd $HOmE
mkdir installer
git clone git@bitbucket.org:ddchavan/microcloud-installer.git
git status
