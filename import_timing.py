#!/usr/bin/env python
"""Code taken from email on numpy list 2008-07-04.  Original auther
was: Andrew Dalke <dalke at dalkescientific dot com>.

"""

import time
from numpy import nan

import argparse

seen = set()
import_order = []
elapsed_times = {}
import_level = 0
parent = None
children = {}

def new_import(name, globals={}, locals={}, fromlist=[], level=-1):
    global import_level, parent
    if name in seen:
        return old_import(name, globals, locals, fromlist)
    seen.add(name)
    import_order.append((name, import_level, parent))
    t1 = time.time()
    old_parent = parent
    parent = name
    import_level += 1
    module = old_import(name, globals, locals, fromlist)
    import_level -= 1
    parent = old_parent
    t2 = time.time()
    elapsed_times[name] = t2-t1
    return module

# Use our own import function
old_import = __builtins__.__import__
__builtins__.__import__ = new_import

def build_parents(import_order):
    parents = {}
    for name, import_level, parent in import_order:
        parents[name] = parent
    return parents

def print_results(import_order, elapsed_times, parents):
    print "== Tree =="
    for name, import_level, parent in import_order:
        print "%s%s: %.3f (%s)" % (" "*import_level, name, 
                                   elapsed_times.get(name, nan), parent)

    print "\n"
    print "== Slowest (including children) =="
    slowest = sorted((t, name) for (name, t) in elapsed_times.items())[-20:]
    for elapsed_time, name in slowest[::-1]:
        print "%.3f %s (%s)" % (elapsed_time, name, parents[name])

def main(argv=None):
    desc = 'Time imports of a module recursively.'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('module_name', nargs='?', default='numpy',
                        help='name of module to time')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='print out some debugging info')
    args = parser.parse_args()

    cmd = "__import__('%s')" % args.module_name
    if args.debug:
        print '== Debug info =='
        print 'dir():', dir()
        print 'cmd:', cmd
        print

    eval(cmd, globals(), locals())

    parents = build_parents(import_order)
    print_results(import_order, elapsed_times, parents)

if __name__ == '__main__':
    main()
