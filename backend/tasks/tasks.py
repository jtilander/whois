from config import huey
import sys


@huey.task()
def count_beans(num):
    print >> sys.stderr, '-- counted %s beans --' % num
    return num
