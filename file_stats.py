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

To execute the file_stats script, if file_stats.py is executable, you
can use this form on the command-line:
    ./file_stats.py [options]

If file_stats.py is not executable, use this form:
    python file_stats.py [options]

Find stats on all Nifti and Analyze files in the users 'data' directory:
    ./file_stats.py ~/data

Find stats on all Nifti files only:
    ./file_stats.py ~/data --patterns *.nii
OR:
    ./file_stats.py ~/data -p *.nii

Find stats on all files with 'foo' in their name:
    ./file_stats.py -p *foo* ~/data

Find stats and print 3 largest files matching the pattern:
    ./file_stats.py -n 3 ~/data/nifti-nih

Find duplicate files with extension .nii.gz (SLOW):
    ./file_stats.py -p *.nii.gz --md5 ~/data

Run file_stats on multiple directories:
    ./file_stats.py -p *.nii.gz ~/data/pype-tut ~/data/nipype-tutorial

Skip selected directories with the -d or --skip-dirs option:
    ./file_stats.py ~/data -d ~/data/pype-tut/fb1-raw-study/mgh-101*

Support for wildcards.  Search all directories in ~/data/pype-tut:
    ./file_stats.py ~/data/pype-tut/*

"""

import os
import sys
import fnmatch
import locale
import shlex

# the md5 module is deprecated in Python 2.6, but hashlib is only
# available as and external package for versions of python before 2.6.
# Both md5 algorithms appear to return the same result.
try:
    from hashlib import md5
except ImportError:
    from md5 import md5

import numpy as np

import argparse

# XXX These are currently unused.  Consider deletion.
nifti_pattern = '*.nii*'
analyze_pattern = '*.img*'
zip_pattern = '*.gz;*.zip;*.bz2'

def _hash_file(filename):
    """Calculate hexdigest of the contents of filename.

    Hashes the file contents, not the filename.  Uses md5 hash.

    Returns
    -------
    hexdigest : string

    """

    md5obj = md5()
    fp = file(filename, 'rb')
    md5obj.update(fp.read())
    fp.close()
    return md5obj.hexdigest()

def file_hashes(file_list):
    """Calculate md5 hashes for all files in file_list.

    This can be slow, depending on size of the list.
 
    Returns
    -------
    hashed_files : dict
        Dictionary where the keys are the md5 hashes and the values
        are a list of all filenames that match that md5 hash.

    """

    dct = {}
    for fn in file_list:
        sys.stdout.write('.')
        sys.stdout.flush()
        hsh = _hash_file(fn)
        if hsh in dct:
            dct[hsh].append(fn)
        else:
            dct[hsh] = [fn]
    return dct

def find_duplicate_files(hash_dict):
    """Print out any duplicate files from the hashed dictionary, hash_dict.
    
    hash_dict is returned from file_hashes function.

    """

    print '\n'
    for key, value in hash_dict.iteritems():
        if len(value) > 1:
            print '\nThese files are identical (%s):' % key
            for item in value:
                print '\t%s' % item


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


def all_dirs(root, patterns='*', skip_dirs='', single_level=False, 
             yield_folders=False):
    """Return path of filenames that match given patterns.
    
    Parameters
    ----------
    root : string
        Root path to begin searching for files that match the patterns
    patterns : string
        Patterns to search for, multiple patterns are separated by semicolon.
        TODO:  Make this a list?
    skip_dirs : string
        Directories to skip/ignore
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
        # Handle skip_dirs.  skip_dirs is a list (or set) of directories to
        # skip.  Each directory in the list should be an absolute
        # path.  For each directory in the skip_dirs, if it matches a
        # directory returned in subdirs (which are subdirectories to
        # be searched next by os.walk), then remove them from the list
        # so they are not searched again.
        to_remove = []
        for sd in skip_dirs:
            for sdir in subdirs:
                if sd in os.path.join(path, sdir):
                    to_remove.append(sdir)
        # Remove the subdirs outside of the above for-loop because
        # there we are iterating over the subdirs and it is not safe
        # to modify a sequence you are iterating over!
        for sdir in to_remove:
            subdirs.remove(sdir)
        if yield_folders:
            files.extend(subdirs)
        files.sort()
        for name in files:
            # We don't care about symlinks.  Ignore any we find.
            if not os.path.islink(os.path.join(path, name)):
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

def _clean_file_list(dir_list):
    """Clean paths and remove duplicates.  Return clean list of files."""
    dirs = []
    for dr in dir_list:
        # remove trailing slashes
        dr = dr.rstrip(os.path.sep)
        # append absolute path
        dirs.append(validate_search_path(dr))
    # remove duplicates
    return set(dirs)

def get_file_list(search_path, patterns, skip_dirs):
    """Search the directories and return list of files that match the
    patterns."""
    filelist = list(all_dirs(search_path, patterns, skip_dirs=skip_dirs))
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
    parser.add_argument('path', nargs='*', 
                        help='The path(s) to generate stats on.')
    parser.add_argument('-p', '--patterns', default='*.nii*;*.img*',
                        help='Filename patterns to search for [*.nii*;*.img*]')
    list_help = 'Print NUM largest files matching the patterns' \
        ' or all files if NUM is not supplied'
    parser.add_argument('-n', '--num', nargs='?', default=False, 
                        help=list_help)
    parser.add_argument('--debug', action='store_true',
                        help='Print out some debugging info.')
    md5_help = 'Find duplicate files. (SLOW) ' \
        'Performs md5 calculation on files and looks for matches'
    parser.add_argument('-m', '--md5', action='store_true', help=md5_help)
    parser.add_argument('-d', '--skip-dirs', nargs='*', default='',
                        help='Ignore/skip these directories')
    parser.add_argument('--doc', action='store_true',
                        help='Print extended documentation.')
    args = parser.parse_args()
    if args.debug:
        print args
    if args.doc:
        print __doc__
        return

    skip_dirs = _clean_file_list(args.skip_dirs)
    path_dirs = _clean_file_list(args.path)
    filelist = []
    for pth in path_dirs:
        tmplist = get_file_list(pth, args.patterns, skip_dirs)
        filelist.extend(tmplist)

    if not filelist:
        # No files to process
        return

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

    # Check for duplicate files
    if args.md5:
        print '\nAnalyzing files, looking for duplicates...'
        hashed_files = file_hashes(filelist)
        find_duplicate_files(hashed_files)

if __name__ == '__main__':
    main()
