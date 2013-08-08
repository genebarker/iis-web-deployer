iis-web-deployer
----------------

IIS Web Deployer - Deploy web application to IIS using Git.

![summary diagram](http://4.bp.blogspot.com/-Q0SscVmaeBI/UfgTSMp7TpI/AAAAAAAABHw/7m9b7iLqYiQ/s400/auto-deployment-system-v2.jpg)

- Git's bin and IIS's inetsrv folders must be in the command path.
- --path must point to a Git repository with its connection to the remote (shared) repository setup.
- Be sure to set HOME=%USERPROFILE% so that Git can find the user's .ssh folder.

For further detail, see the accompanying [Git WinRM Automatic Deployment](http://architect.madman.com/2013/07/git-winrm-automatic-deployment.html) article on my [blog](http://architect.madman.com).