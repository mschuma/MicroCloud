#!/bin/sh

if [[($1 = "") || ($2 = "")]]; then
    echo "Usage: dev_setup.sh <git user.name> <git user.email>"
    exit 1
fi

# Install git

git_version=1.8.1.4
cd $HOME
wget http://git-core.googlecode.com/files/git-$git_version.tar.gz 
tar xvzf git-$git_version.tar.gz 
cd git-$git_version
./configure --prefix=$HOME/git 
make 
make install 
export PATH=$PATH:$HOME/git/bin
cd $HOME
rm -rf git-$git_version
rm git-$git_version.tar.gz

# Configure git user name and email
git config --global user.name=$1
git config --global user.email=$2

# Setup the public key
ssh-keygen
echo "Copy this key to github. Hit enter after copying"
echo
cat $HOME/.ssh/id_rsa.pub
echo
read

# Clone the MicroCloud repo
cd $HOmE
git clone git@github.com:mschuma/MicroCloud.git
git status

# Copy .vimrc
cp .vimrc $HOME/.vimrc
