#!/usr/bin/env python2
# -*- coding:utf-8 -*-

def main():
    for i in xrange(1000):
        a, b = map(int, raw_input().split())
        print a + b

if __name__ == '__main__':
    main()