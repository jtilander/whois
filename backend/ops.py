from tasks.config import huey
from tasks.tasks import count_beans

if __name__ == '__main__':
    for i in xrange(100):
        count_beans(i)
