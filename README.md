MicroCloud
==========

CSC-591-004 MicroCloud Project Repository

Usage
-----
1. **dev_setup.sh**: Script for setting up the development environment.

   + *Requires*: 
    1. `chmod 744` to add execute permission. 
    2. `PATH` to be updated to include `usr/sbin:/sbin:$HOME/git/bin`. This can
        changed by modifying $HOME/.bash_profile

   + *Description*:
    1. Download and install [git][1] ([version 1.8.1.4][2]) locally in $HOME/git            
    2. Setup git [user name][3]/[email][4] (passed as argument)
    3. Start `ssh-keygen` to generate public-private key pair
    4. Prompt to [add public key][7] to github account ($HOME/.ssh/id_rsa.pub)
    5. Clone the [MicroCloud][5] repo
    6. Setup [vimrc][6] (warning! overwrites existing $HOME/.vimrc)
    
   + *Usage*:      `dev_setup.sh <git user.name> <git user.email>`

   + *Example*:    `./dev_setup.sh "foo" "foo@bar.com"`

 [1]: http://code.google.com/p/git-core/downloads/list
 [2]: http://git-core.googlecode.com/files/git-1.8.1.4.tar.gz
 [3]: https://help.github.com/articles/setting-your-username-in-git
 [4]: https://help.github.com/articles/setting-your-email-in-git
 [5]: https://github.com/mschuma/MicroCloud
 [6]: http://vim.wikia.com/wiki/Open_vimrc_file
 [7]: https://help.github.com/articles/generating-ssh-keys
