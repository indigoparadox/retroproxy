#!/usr/bin/env python

import logging
import argparse
from retroproxy.server import RetroHTTPServer

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument( '-s', '--start', action='store', type=int, default=19990100000000 )

    parser.add_argument( '-e', '--end', action='store', type=int, default=19991200000000 )

    parser.add_argument( '-a', '--address', action='store', default='127.0.0.1' )

    parser.add_argument( '-p', '--port', action='store', type=int, default=8888 )

    parser.add_argument( '-v', '--verbose', action='store_true' )

    args = parser.parse_args()

    level = level=logging.INFO
    if args.verbose:
        level = logging.DEBUG
    logging.basicConfig( level=level )
    logger = logging.getLogger( 'main' )

    server = RetroHTTPServer( (args.address, args.port), args.start, args.end )
    logger.info( 'starting server on %s:%d...', args.address, args.port )
    server.serve_forever()

if '__main__' == __name__:
    main()
