#!/usr/bin/env python3

import logging
from retroproxy import create_app

app = create_app()

def main():
    logging.basicConfig( level=logging.INFO )
    logger = logging.getLogger( 'main' )
    
    app.run( host='0.0.0.0', port=80 )

if '__main__' == __name__:
    main()
