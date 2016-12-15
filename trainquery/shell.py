#!/usr/bin/env python
#
# Copyright (C) 2016 ShadowMan
#
import argparse
import logging

QUIET = 35
VERBOSE = 5

def check_args(args):
    if args.verbose >= 2:
        level = VERBOSE
    elif args.verbose == 1:
        level = logging.INFO
    else:
        level = QUIET
    logging.basicConfig(level = level,
                        format = '%(asctime)s %(levelname)-8s %(message)s',
                        datefmt = '%Y-%m-%d %H:%M:%S')

def entry_point():
    parse = argparse.ArgumentParser()
    group = parse.add_mutually_exclusive_group()
    parse.add_argument('-f', '--from', help = 'where are you from')
    parse.add_argument('-t', '--to', help = 'where are you go')
    parse.add_argument('-d', '--date', help='time of departure')
    group.add_argument('-v', '--verbose', help = 'output verbosity', action = 'count')
    group.add_argument('-q', '--quiet', help = 'simple output', action = 'store_true')

    check_args(parse.parse_args())