
import logging
import re
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlunsplit

import requests

from retroproxy.filter import RetroFilter

HTML_TYPE_PATTERN = re.compile( r'^([a-zA-Z]*/(html|HTML)).*' )
HEADER_ORIG_PATTERN = re.compile( r'^[Xx]-[Aa]rchive-[Oo]rig-(.*)$' )

class RetroHTTPHandler( BaseHTTPRequestHandler ):

    def make_archive_url( self, scheme, host, path ):
        archive_url = 'https://web.archive.org/web/{}/{}'.format(
            self.server.archive_start,
            urlunsplit( (scheme, host, path, None, None ) ) )
        return archive_url

    def translate_archive_headers( self, headers ):
        # Grab the original headers from the archive.
        for hdr, val in headers.items():
            match = HEADER_ORIG_PATTERN.match( hdr )
            if match:
                key = match.groups()[0]
                self.server.logger.info(
                    'orig header "%s": "%s"', key, val )
                if key.lower() == 'content-length':
                    # Skip content length header, as it might not be
                    # accurate.
                    continue
                yield key, val

    def do_GET( self ):

        archive_url = self.make_archive_url(
            'http', self.headers.get( 'Host' ), self.path )
        response = requests.get( archive_url )

        self.server.logger.info(
            'response: %d', response.status_code )
        if 404 == response.status_code:
            self.send_response( 404 )
            return

        # Don't send real date. Let that come from x-archive-orig-date.
        self.send_response_only( 200 )

        for header, value in self.translate_archive_headers( response.headers ):
            self.send_header( header, value )

        # Send the body.
        content_type = response.headers['content-type']
        content_type_match = HTML_TYPE_PATTERN.match( content_type )
        body_out = None
        if content_type_match:
            soup = RetroFilter( response.text, self.server.server_port )
            soup.process_html_links()
            soup.process_html_imgs()
            soup.process_html_forms()
            soup.process_html_scripts()
            soup.cleanup_archive_org()
            body_out = str( soup ).encode( 'utf-8' )
        else:
            self.server.logger.info(
                'unrecognized mimetype: %s', content_type )
            body_out = response.content

        self.send_header(
            b'content-length', str( len( body_out ) ).encode( 'utf-8' ) )
        self.end_headers()
        self.wfile.write( body_out )

class RetroHTTPServer( HTTPServer ):

    def __init__( self, server_address, archive_start, archive_end ):
        super().__init__( server_address, RetroHTTPHandler )
        self.server_port = server_address[1]
        self.archive_start = archive_start
        self.archive_end = archive_end
        self.logger = logging.getLogger( 'retroproxy' )
