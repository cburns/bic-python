#!/usr/bin/env python
"""A script to answer these questions about data files used at the
BIC: how many, how large, and what type of files.

Requires
--------
Python 2.4 or greater

argparse.py 
    This can be installed via yum: yum search python-argparse
    Or from the website: http://code.google.com/p/argparse/

"""

import os
import fnmatch
import locale
import argparse

nifti_pattern = '*.nii*'
analyze_pattern = '*.img*'
zip_pattern = '*.gz;*.zip;*.bz2'

def file_sizes(file_list):
    """Get the sum and mean of filelist.
    
    Returns
    -------
    sum, mean
    
    """
    size_list = map(os.path.getsize, file_list)
    size_sum = sum(size_list)
    size_mean = size_sum / float(len(size_list))
    return size_sum, size_mean

def all_dirs(root, patterns='*', single_level=False, yield_folders=False):
    """Return path of filenames that match given patterns.
    
    Parameters
    ----------
    root : string
        Root path to begin searching for files that match the patterns
    patterns : string
        Patterns to search for, multiple patterns are separated by semicolon.
        TODO:  Make this a list!
    single_level : {True, False}
        TODO: Change to recurse and reverse logic below!
    yield_folders : {True, False}
        TODO: Understand this param.

    Notes
    -----
    Code taken from Python Cookbook Recipe 2.16

    """
    patterns = patterns.split(';')
    for path, subdirs, files in os.walk(root):
        if yield_folders:
            files.extend(subdirs)
        files.sort()
        for name in files:
            for pattern in patterns:
                if fnmatch.fnmatch(name, pattern):
                    yield os.path.join(path, name)
                    break
        if single_level:
            break

def validate_search_path(path):
    """Validate path passed in at command line."""
    search_path = os.path.abspath(os.path.expanduser(path))
    if not os.path.exists(search_path):
        msg = 'Path "%s" does not exist!' % search_path
        raise IOError(msg)
    return search_path

def get_file_list(search_path, patterns):
    """Search the directories and return list of files that match the
    patterns."""
    filelist = list(all_dirs(search_path, patterns))
    return filelist
    

if __name__ == '__main__':
    desc = 'Script to acquire some statistics on images used at the BIC'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('path', help='the path to generate stats on')
    parser.add_argument('-p', '--patterns', default='*.nii*;*.img*',
                        help='filename patterns to search for')
    parser.add_argument('-l', '--list', action='store_true',
                        help='print all files matching the patterns')

    args = parser.parse_args()
    print args

    search_path = validate_search_path(args.path)
    filelist = get_file_list(search_path, args.patterns)
    # TODO: parameterize
    asum, amean = file_sizes(filelist)
    
    if args.list:
        print filelist

    locale.setlocale(locale.LC_ALL, "")
    print 'Total number of images:', len(filelist)
    print 'Total size of nifti and analyze images:', \
        locale.format('%d', asum, True)
    print 'Average size:', locale.format('%d', amean, True) 
