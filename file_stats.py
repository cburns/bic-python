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
    size_list : list
        List containing (file_size, file_name) pairs.
    
    """
    #size_list = map(os.path.getsize, file_list)
    #[(os.path.getsize(fn), fn) for fn in filelist]
    lst = []
    # calculate maximum filename length so we know how large to make
    # our recarray.
    max_len = 0
    for fn in file_list:
        sz = int(os.path.getsize(fn))
        lst.append((sz, fn))
        if len(fn) > max_len:
            max_len = len(fn)
    # sort smallest to largest (in-place)
    lst.sort()
    # Create an array so we can easily access the columns later
    tmp_array = np.array(lst)
    #fn_dtype = 'S%d' % max_len
    fn_dtype = tmp_array.dtype
    # Create a record array so we can access the array columns via field names.
    size_array = np.recarray((len(lst),), dtype = [('size', 'int32'), 
                                                   ('filename', fn_dtype)])
    size_array['size'][:] = tmp_array[:, 0]
    size_array['filename'][:] = tmp_array[:, 1]
    return size_array

    # assert X['size'].max() == X['size'][-1]

    """
    In [107]: X[:, 0].astype(int)
    Out[107]: array([   41312,   344416,   902981,   902981, 30966112, 42338528])

    In [130]: ra = np.recarray((6,), dtype=[('size', 'int32'), ('filename', 'S51')])

    In [116]: strarr = np.zeros(6, dtype='|S51')

    In [117]: Y[:, 1]
    Out[117]: 
    array(['/Users/cburns/data/nifti-nih/minimal.nii',
           '/Users/cburns/data/nifti-nih/zstat1.nii',
           '/Users/cburns/data/nifti-nih/avg152T1_LR_nifti.nii',
           '/Users/cburns/data/nifti-nih/avg152T1_RL_nifti.nii',
           '/Users/cburns/data/nifti-nih/filtered_func_data.nii',
           '/Users/cburns/data/nifti-nih/newsirp_final_XML.nii'], 
          dtype='|S51')

    In [118]: strarr[:] = Y[:, 1]

    In [133]: ra['size'][:] = Y[:, 0]
    In [136]: ra['filename'][:] = Y[:, 1]


    """
    """
    size_sum = sum(size_list)
    size_mean = size_sum / float(len(size_list))
    return size_sum, size_mean
    """

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

def _format_output(fmt, val):
    return locale.format(fmt, val, True).rjust(20)

def print_stats(filelist, patterns):
    """Print file statistics for files in filelist."""
    # Get file sizes
    size_array = file_sizes(filelist)
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
    print 'Number of files: ', len(filelist)
    print 'Total size:    ', locale.format('%d', asum, True).rjust(20)
    print 'Average size:  ', locale.format('%.2f', amean, True).rjust(20)
    print 'Minimum size:  ', _format_output('%d', amin)
    print 'Maximum size:  ', _format_output('%d', amax)
    print 'Standard dev:  ', _format_output('%.2f', astd)
    print 'Variance:      ', _format_output('%.2f', avar) 


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
    parser.add_argument('-l', '--list', action='store_true',
                        help='print all files matching the patterns')
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
    if args.list:
        # TODO: add nargs to this argument and print out # largest files
        for item in filelist:
            print item

    print_stats(filelist, args.patterns)

if __name__ == '__main__':
    main()
