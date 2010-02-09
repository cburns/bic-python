#!/usr/bin/env python
"""Remove generated python files when checking out a new branch in
git.  Specifically this removes .pyc and .py~ files.  This prevents
confusion and possible import problems with switching between
different branches.

To use:

1) copy this file to your <repository>/.git/hooks directory

2) rename to 'post-checkout', removing the .py extension (otherwise
git will not execute it)

3) make the script executable: 'chmod a+x post-checkout'

This will be called everytime 'git checkout <branch>' is executed.

"""

import os

extensions = ('.pyc', '.py~')

def remove_generated(arg, dirname, fnames):
    """Remove generated files from this directory."""
    for filename in fnames:
        if filename.endswith(extensions):
            filepath = os.path.join(dirname, filename)
            os.remove(filepath)

if __name__ == '__main__':
    os.path.walk(os.curdir, remove_generated, None)
