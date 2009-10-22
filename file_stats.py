#!/usr/bin/env python
"""A script to answer these questions about data files used at the
BIC: how many, how large, and what type of files.  Given a search path
and a file pattern, file all files that match the pattern(s) and
report there total and average file sizes.  The default is to report
on Nifti and Analyze files, patterns=*.nii*;*.img*

For usage, see command-line help:
    $ ./file_stats.py -h

Requires
--------
Python 2.4 or greater

argparse.py 
    This can be installed via yum:  yum search python-argparse
    Or from the website:  http://code.google.com/p/argparse/

Examples
--------

Find stats on all Nifti and Analyze files in the users 'data' directory:
    ./file_stats.py ~/data

Find stats on all Nifti files only:
    ./file_stats.py ~/data --patterns *.nii
OR:
    ./file_stats.py ~/data -p *.nii

Find stats on all files with 'foo' in their name:
    ./file_stats.py ~/data -p *foo*

Find stats and print 3 largest files matching the patter:
    ./file_stats.py ~/data/nifti-nih -n 3

"""

import os
import sys
import fnmatch
import locale
import shlex

import numpy as np

import argparse

nifti_pattern = '*.nii*'
analyze_pattern = '*.img*'
zip_pattern = '*.gz;*.zip;*.bz2'

def file_sizes(file_list):
    """Get the file size for each file in the list.
    
    Returns
    -------
    size_array : numpy.recaray
        Fields of the recarray are 'size', 'filename'.
        To access size of first file:  size_array['size'][0]
        To access all sizes:  size_array['size']
    
    """
    lst = []
    for fn in file_list:
        sz = int(os.path.getsize(fn))
        lst.append((sz, fn))
    # sort smallest to largest (in-place)
    lst.sort()
    # Create an array so we can easily access the columns later
    tmp_array = np.array(lst)
    fn_dtype = tmp_array.dtype
    # Create a record array so we can access the array columns via field names.
    size_array = np.recarray((len(lst),), dtype = [('size', 'int32'), 
                                                   ('filename', fn_dtype)])
    size_array['size'][:] = tmp_array[:, 0]
    size_array['filename'][:] = tmp_array[:, 1]
    # If these fail, then something went wrong
    assert size_array['size'].max() == size_array['size'][-1]
    assert size_array['size'].min() == size_array['size'][0]
    return size_array


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

def _format_output(val, fmt='%d', rjust=20):
    return locale.format(fmt, val, True).rjust(rjust)

def print_stats(size_array, patterns):
    """Print file statistics for files in filelist."""
    # Calculate some stats
    asum = size_array['size'].sum()
    amean = size_array['size'].mean()
    amin = size_array['size'].min()
    amax = size_array['size'].max()
    astd = size_array['size'].std()
    avar = size_array['size'].var()
    # set internationalization settings to user defaults
    locale.setlocale(locale.LC_ALL, "")
    print 'Patterns matched:', patterns
    print 'Number of files: ', _format_output(len(size_array), rjust=18)
    print 'Total size:    ', _format_output(asum)
    print 'Average size:  ', _format_output(amean)
    print 'Minimum size:  ', _format_output(amin)
    print 'Maximum size:  ', _format_output(amax)
    print 'Standard dev:  ', _format_output(astd)
    print 'Variance:      ', _format_output(int(avar))

def print_files(size_array):
    """Print given files and their sizes."""
    for sz, fn in size_array:
        print _format_output(sz, rjust=16), ' ', fn

def main(argv=None):
    if argv is None:
        # Look at the FILE_STATS_ARGS environment variable for more arguments.
        # Stole this from Robert Kern's grin
        env_args = shlex.split(os.getenv('FILE_STATS_ARGS', ''))
        argv = [sys.argv[0]] + env_args + sys.argv[1:]
    desc = 'Script to acquire some statistics on images used at the BIC'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('path', help='the path to generate stats on')
    parser.add_argument('-p', '--patterns', default='*.nii*;*.img*',
                        help='filename patterns to search for [*.nii*;*.img*]')
    list_help = 'Print NUM largest files matching the patterns' \
        ' or all files if NUM is not supplied'
    parser.add_argument('-n', '--num', nargs='?', default=False,
                        help=list_help)
    parser.add_argument('-d', '--debug', action='store_true',
                        help='print out some debugging info')
    parser.add_argument('--doc', action='store_true',
                        help='print extended documentation')
    args = parser.parse_args()
    if args.debug:
        print args
    if args.doc:
        print __doc__
        return

    search_path = validate_search_path(args.path)
    filelist = get_file_list(search_path, args.patterns)
    # Get file sizes
    size_array = file_sizes(filelist)

    print_stats(size_array, args.patterns)

    if args.num is not False:
        if args.num is None:
            # print whole list
            selected = size_array
        else:
            # print only requested amount
            n = int(args.num)
            selected = size_array[-n:]
        print
        print_files(selected)

if __name__ == '__main__':
    main()
