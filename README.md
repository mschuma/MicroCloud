MicroCloud
==========

CSC-591-004 MicroCloud Project Repository

 1. **dev_setup.sh**: Script for setting up the development environment.

    *Requires*: Run `chmod 744` to add execute permission. 

    *Description*:
    a. Download and install [git][1] ([version 1.8.1.4][2]) locally in 
            $HOME/git
    b. Setup git [user name][3]/[email][4] (passed as argument)
    c. Start `ssh-keygen` to generate public-private key pair
    d. Prompt to [add pubic key][7] to github account ($HOME/.ssh/id_rsa.pub)
    e. Clone the [MicroCloud][5] repo
    f. Setup [vimrc][6] (*warning*! overwrites existing $HOME/.vimrc)
    
    *Usage*:      `dev_setup.sh <git user.name> <git user.email>`

    *Example*:    `./dev_setup.sh "foo" "foo@bar.com"`

 [1]: http://code.google.com/p/git-core/downloads/list
 [2]: http://git-core.googlecode.com/files/git-1.8.1.4.tar.gz
 [3]: https://help.github.com/articles/setting-your-username-in-git
 [4]: https://help.github.com/articles/setting-your-email-in-git
 [5]: https://github.com/mschuma/MicroCloud
 [6]: http://vim.wikia.com/wiki/Open_vimrc_file
 [7]: https://help.github.com/articles/generating-ssh-keys
