
import os
import glob

def all_files(pattern, search_path, pathsep=os.pathsep):
    for path in search_path.split(pathsep):
        for match in glob.glob(os.path.join(path, pattern)):
            yield match

def file_sizes(file_list):
    size_list = map(os.path.getsize, file_list)
    size_sum = sum(size_list)
    size_mean = size_sum / float(len(size_list))
    return size_sum, size_mean


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


