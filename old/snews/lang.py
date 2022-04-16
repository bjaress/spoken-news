#! /usr/bin/env python3

from unidecode import unidecode
import sys

def main():
    for line in sys.stdin:
        print(unidecode(line), end='')


if __name__ == '__main__':
    main()

