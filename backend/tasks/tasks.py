from config import huey
import sys


@huey.task()
def count_beans(num):
    num = num * 100
    print >> sys.stderr, '-- counted %s beans --' % num
    return num
