# <-- Run aws-interface view with HTTP server -->
# <-- You can access aws-interface with [localhost] -->
# $ python run.py 80
import sys


def main(port):
    print('port:', port)
    raise NotImplementedError()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        print('No argument <port>, default port is 80')
        main('80')