import requests
import os
import argparse
import sys
import logging
import json
import base64


from webops_py.restapi import (get_clean_host, get_ops_list, get_op_meta, execute_op, 
                                OpException,HTTPException)
from webops_py.parsers import get_parser

"""

parser.add_argument('integers', metavar='N', type=int, nargs='+',
                   help='an integer for the accumulator')
parser.add_argument('--sum', dest='accumulate', action='store_const',
                   const=sum, default=max,
                   help='sum the integers (default: find the max)')

args = parser.parse_args()
print args.accumulate(args.integers)
"""

from colorlog import ColoredFormatter
  
  
def setup_logger():
    """
    Returns a logger with a default ColoredFormatter.
    """
    formatter = ColoredFormatter(
        #"%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
        "%(log_color)s%(levelname)-8s %(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'red',
        }
    )
  
    logger = logging.getLogger('example')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
  
    return logger


logger = setup_logger()

def exit_with_error(err):
    logger.error('')
    logger.error(err)

    #print "\n|webops| (error) sorry .. something went wrong :(  \n"
    #print "\t"+err
    #print
    sys.exit(1)   



def print_ops_list(ops):
    for x in ops:
        print x['id']
        print x['description']
        print


def print_op_meta(x):
    print
    print x['id']
    print x['name']
    print x['description']
    print    
    print "PARAMETERS"
    print
    for p in x['parameters']:
        print p
        print "Description:", x['parameters'][p]['description']
        print "Type:",x['parameters'][p]['type']
        print "Required:",x['parameters'][p]['required']
        print



def run_op(host, op, op_args, outfile=None):          
    try:
        result_data = execute_op(host, op, op_args, outfile)
        logger.info("Result: " + str(result_data["result"]))
    
    except OpException as e:

        for x in  e.errors_data:
            if type(e.errors_data[x]) == list:
                logger.error(x + ":" + ",".join(e.errors_data[x]))
            else:
                logger.error(x + ":" + e.errors_data[x])

        sys.exit(1)   

    except HTTPException as e:
        
        logger.error("HTTP ERROR:" + str(e.response.status_code))
        if e.response.status_code == 404:
            logger.error("%s not found" % op)

        sys.exit(1)
        
        


parser = argparse.ArgumentParser(description='Webops command line utility', add_help=True)
parser.add_argument('--host',  type=str, nargs='?',
                   help='webops host name and port or ip address and port')


parser.add_argument('--outfile',  type=str, nargs='?', default=None,
                   help='file output name')

parser.add_argument('--list', action="store_true", default=False,
                   help='print list')

parser.add_argument('--meta', action="store_true", default=False,
                   help='print op meta')

parser.add_argument('--run', action="store_true", default=False,
                   help='run op')

parser.add_argument('op', type=str, nargs='?', 
                   help='op name to operate on')


parser.add_argument('opargs', nargs=argparse.REMAINDER)



args = parser.parse_args()
host =  args.host
if 'WEBOPS_HOST' in os.environ:
    host = os.environ['WEBOPS_HOST']

if not host:
    exit_with_error('no WEBOPS_HOST')

logger.info("webops operating on %s" % host)

if args.list:
    lst = get_ops_list(host)
    print_ops_list(lst)



if args.meta:
    if not args.op:
        exit_with_error("meta requires an op.")
    meta = get_op_meta(host, args.op)
    print_op_meta(meta)

if args.run:
    if not args.op:
        exit_with_error("meta requires an op.")
    run_op(host, args.op, args.opargs, outfile=args.outfile)







