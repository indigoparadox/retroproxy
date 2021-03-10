
import logging
import unittest
import os
import sys
import threading
import socket
import time
from unittest.mock import Mock, MagicMock

import requests

sys.path.insert( 0, os.path.dirname( os.path.dirname( __file__ ) ) )

import retroproxy.server

# The header names have been normalized to lower-case, as requests makes
# them case-insensitive anyway.
TEST_GOOGLE_COM_HEADERS = {
    'server': 'nginx/1.19.5',
    'date': 'Wed, 10 Mar 2021 05:03:09 GMT',
    'content-type': 'text/html; charset=utf-8',
    'transfer-encoding': 'chunked',
    'connection': 'keep-alive',
    'x-archive-orig-server': 'Medusa/1.10',
    'x-archive-orig-content-length': '1646',
    'x-archive-orig-last-modified': 'Fri, 08 Jan 1999 22:02:15 GMT',
    'x-archive-orig-date': 'Sun, 17 Jan 1999 03:24:01 GMT',
    'x-archive-guessed-content-type': 'text/html',
    'x-archive-guessed-charset': 'utf-8',
    'memento-datetime': 'Sun, 17 Jan 1999 03:27:27 GMT',
    'link': '<http://www.google.com:80/>; rel="original", ' + \
        '<https://web.archive.org/web/timemap/link/http://www.google.com' + \
        ':80/>; rel="timemap"; type="application/link-format", ' + \
        '<https://web.archive.org/web/http://www.google.com:80/>; ' + \
        'rel="timegate", ' + \
        '<https://web.archive.org/web/19981111184551/http://google.com:80/>;' + \
        ' rel="first memento"; datetime="Wed, 11 Nov 1998 18:45:51 GMT", ' + \
        '<https://web.archive.org/web/19981202230410/http://www.google.com' + \
        ':80/>; rel="prev memento"; datetime="Wed, 02 Dec 1998 23:04:10 GMT' + \
        '", <https://web.archive.org/web/19990117032727/http://www.google.com' + \
        ':80/>; rel="memento"; datetime="Sun, 17 Jan 1999 03:27:27 GMT", ' + \
        '<https://web.archive.org/web/19990117102024/http://www.google.com' + \
        ':80/>; rel="next memento"; datetime="Sun, 17 Jan 1999 10:20:24 GMT' + \
        '", ' + \
        '<https://web.archive.org/web/20210310044735/https://www.google.com' + \
        '/>; rel="last memento"; datetime="Wed, 10 Mar 2021 04:47:35 GMT"',
    'content-security-policy': '"default-src \'self\' \'unsafe-eval\' ' + \
        '\'unsafe-inline\' data: blob: archive.org web.archive.org ' + \
        'analytics.archive.org pragma.archivelab.org"',
    'x-archive-src': 'INA-HISTORICAL-2007-GROUP-KUR-20100812000000-00000-c' + \
        '/INA-HISTORICAL-EMBEDS-1999-GROUP-AAD-20100812000000-00000.arc.gz',
    'server-timing': 'exclusion.robots;dur=0.425385, ' + \
        'exclusion.robots.policy;dur=0.373311, ' + \
        'RedisCDXSource;dur=29.672230, esindex;dur=0.044715, ' + \
        'LoadShardBlock;dur=1650.125276, ' + \
        'PetaboxLoader3.datanode;dur=746.413482, ' + \
        'CDXLines.iter;dur=347.305569, load_resource;dur=38.436892, ' + \
        'PetaboxLoader3.resolve;dur=27.308152',
    'x-app-server': 'wwwb-app201',
    'x-ts': '200',
    'x-tr': '2145',
    'x-location': 'All',
    'x-cache-Key':
        'httpsweb.archive.org/web/19990117032727/http://www.google.com/US',
    'x-rl': '0',
    'x-na': '0',
    'x-page-cache': 'EXPIRED',
    'x-nid': '-',
    'content-encoding': 'gzip'
}

TEST_GOOGLE_COM_BODY = ''
with open( 'tests/google.html', 'r' ) as test_google_com_file:
    TEST_GOOGLE_COM_BODY = test_google_com_file.read()

class TestServer( unittest.TestCase ):

    def setUp( self ):
        self.logger = logging.getLogger( 'test_server' )
        self.logger.setLevel( logging.INFO )
        self.server_port = 8888

        retroproxy.server.requests = Mock()
        retroproxy.server.requests.get.return_value = Mock()
        self.get = retroproxy.server.requests.get.return_value
        self.get.headers.items.return_value = TEST_GOOGLE_COM_HEADERS.items()
        self.get.headers.__getitem__ = Mock(
            side_effect=lambda x: TEST_GOOGLE_COM_HEADERS[x] )
        self.get.text = TEST_GOOGLE_COM_BODY

        self.server = retroproxy.server.RetroHTTPServer(
            ('localhost', self.server_port), 19990100000000, 19991200000000 )
        self.server_thread = \
            threading.Thread( target=self.server.serve_forever )
        self.logger.info( 'starting server...' )
        self.server_thread.start()

    def tearDown( self ):
        self.logger.info( 'stopping server...' )
        self.server.shutdown()

    def test_server_request( self ):

        socket.getaddrinfo = lambda w, x, y, z: \
            [(socket.AF_INET, socket.SOCK_STREAM, 6, '',
                ('127.0.0.1', self.server_port))]

        res = requests.get( 'http://google.com' )

        self.assertEqual( res.headers['server'], 'Medusa/1.10' )
        self.assertEqual( res.headers['date'], 'Sun, 17 Jan 1999 03:24:01 GMT' )
        #self.assertEqual( res.headers['content-length'], '1646' )
        self.assertEqual( res.headers['last-modified'], 'Fri, 08 Jan 1999 22:02:15 GMT' )

        retroproxy.server.requests.get.assert_called_once_with(
            'https://web.archive.org/web/19990100000000/http://google.com/' )

        print( res.text )
