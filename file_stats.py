
import os
import glob
import fnmatch
import locale

def all_files(pattern, search_path, pathsep=os.pathsep):
    for path in search_path.split(pathsep):
        for match in glob.glob(os.path.join(path, pattern)):
            yield match

def file_sizes(file_list):
    size_list = map(os.path.getsize, file_list)
    size_sum = sum(size_list)
    size_mean = size_sum / float(len(size_list))
    return size_sum, size_mean

def all_dirs(root, patterns='*', single_level=False, yield_folders=False):
    """Python Cookbook Recipe 2.16
    patterns is a semicolon-separated string.
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

if __name__ == '__main__':
    pattern = '*.nii*'
    search_path = os.path.abspath(os.path.expanduser('~/data'))
    file_list = list(all_files(pattern, search_path))
    pattern = '*.img*'
    anas = list(all_files(pattern, search_path))
    for item in anas:
        file_list.append(item)
    print file_list
    asum, amean = file_sizes(file_list)
    
    print 'total size:', asum
    print 'average size:', amean

    newlist = list(all_dirs(search_path, patterns='*.nii*;*.img*'))
    asum, amean = file_sizes(newlist)
    #print 'total size:', asum
    #print 'average size:', amean
    
    locale.setlocale(locale.LC_ALL, "")
    print 'Total size of nifti and analyze images:', \
        locale.format('%d', asum, True)
    print 'Average size:', locale.format('%d', amean, True) 
