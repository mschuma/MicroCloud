#!/bin/sh

# Requires the PATH variable to be updated 
# Can be done by modifying $HOME/.bash_profile
# PATH=$PATH:$HOME/bin:/usr/sbin:/sbin:$HOME/git/bin

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
cd $HOME
rm -rf git-$git_version
rm git-$git_version.tar.gz

# Configure git user name and email
git config --global user.name "$1"
git config --global user.email "$2"
git config --global push.default simple

# Setup the public key
ssh-keygen
echo "Copy this key to github. Hit enter after copying"
echo
cat $HOME/.ssh/id_rsa.pub
echo
read

# Clone the MicroCloud repo
cd $HOME
git clone git@github.com:mschuma/MicroCloud.git

# Checkout the installer branch. 
# git checkout -b installer --track origin/installer

git_repo_name="MicroCloud"
if [ -d $git_repo_name ]; then
    cd MicroCloud

    if [ -f ".vimrc" ]; then    
        # Copy .vimrc
        cp .vimrc $HOME/.vimrc
    fi
fi
