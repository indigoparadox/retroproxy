
import re
import logging
from urllib.parse import urlparse, urlunsplit

from bs4 import BeautifulSoup, Comment

ARCHIVE_PATTERN = re.compile(
    r'^(https?://web.archive.org)?/web/[0-9a-z_]*/' )
URL_PORT_PATTERN = re.compile( r'(?P<netloc>.*?)(?P<port>:[0-9]*)?$' )
FILE_ARCHIVED_PATTERN = re.compile(
    r'<!--.*FILE\s*ARCHIVED\s*ON.*AND\s*RETRIEVED\s*' + \
    r'FROM\s*THE\s*INTERNET\s*ARCHIVE.*?-->' )

class RetroFilter( BeautifulSoup ):

    def __init__( self, text, url_port, *args, **kwargs ):
        super().__init__( text, 'html.parser', *args, **kwargs )
        self.url_port = str( url_port )
        self.logger = logging.getLogger( 'retroproxy' )

    def fix_netloc_port( self, url_in ):

        ''' Given a URL, insert the given listening port next to the host. '''

        nl_url = urlparse( url_in )
        if nl_url.netloc:
            #netloc_match = URL_PORT_PATTERN.match( nl_url.netloc )
            #print( netloc_match.groupdict() )
            #print( nl_url.hostname )
            netloc = nl_url.hostname + ':' + self.url_port
            return urlunsplit(
                (nl_url.scheme, netloc, nl_url.path,
                nl_url.query, nl_url.fragment) )

        else:
            return url_in

    def cleanup_archive_org( self ):

        for comment in self.find_all( string=lambda x: isinstance( x, Comment ) ):
            comment : Comment
            if 'INTERNET ARCHIVE' in comment or \
            'playback timings' in comment:
                comment.extract()
                continue

            if 'BEGIN WAYBACK TOOLBAR' in comment:
                next_tag = comment.next_element
                while 'END WAYBACK TOOLBAR' not in next_tag:
                    this_tag = next_tag
                    next_tag = next_tag.next_sibling
                    this_tag.extract()
                next_tag.extract() # Get rid of the "END" comment.
                comment.extract() # Get rid of the "BEGIN" comment.

    def process_html_scripts( self ):

        # Fix for static CSS.
        # TODO: Should these just be stripped?
        for link in self.findAll( 'link' ):
            try:
                if link['href'].startswith( '/_static/' ):
                    #link['href'] = \
                    #    'https://web.archive.org{}'.format( link['href'] )
                    self.logger.debug( 'removing link' )
                    link.extract()
                else:
                    link['href'] = self.fix_netloc_port( link['href'] )
            except Exception as exc:
                self.logger.warning( exc )

        # Strip out archive modernity hacks.
        for script in self.findAll( 'script' ):
            if 'src' in script.attrs and (
            'client-rewrite.js' in script.attrs['src'] or \
            'wbhack.js' in script.attrs['src'] or \
            'wombat.js' in script.attrs['src'] or \
            'playback.bundle.js' in script.attrs['src'] or \
            'archive.org/includes/analytics.js' in script.attrs['src'] ):
                self.logger.debug( 'removing script' )
                script.extract()
                continue

            if 'wbhack.' in str( script ) or \
            'WB_wombat_Init' in str( script ) or \
            '__wbhack.init' in str( script ) or \
            '__wm.wombat' in str( script ) or \
            'archive_analytics.values' in str( script ):
                self.logger.debug( 'removing script' )
                script.extract()
                continue

    def process_html_links( self ):

        for a in self.findAll( 'a' ):
            try:
                #self.logger.info( a['href'] )
                href = ARCHIVE_PATTERN.sub( '', a['href'] )
                self.logger.debug( '%s became: %s', a['href'], href )
                a['href'] = href

                # Add our listening port to the netloc.
                a['href'] = self.fix_netloc_port( a['href'] )
            except Exception as exc:
                self.logger.warning( exc )

        # Fix for optional base tag.
        for base in self.findAll( 'base' ):
            try:
                base['href'] = ARCHIVE_PATTERN.sub( '', base['href'] )

                base['href'] = self.fix_netloc_port( base['href'] )
            except Exception as exc:
                self.logger.warning( exc )

    def process_html_imgs( self ):

        # Fix for images relative to web.archive.org.
        #for img in self.findAll( 'img' ):
        #    if img['src'].startswith( '/web/' ):
        #        img['src'] = 'https://web.archive.org{}'.format( img['src'] )

        # Fix for all images.
        for img in self.findAll( 'img' ):
            try:
                img['src'] = ARCHIVE_PATTERN.sub( '', img['src'] )
                img['src'] = self.fix_netloc_port( img['src']  )
            except Exception as exc:
                self.logger.warning( exc )

    def process_html_forms( self ):

        for form in self.findAll( 'form' ):
            try:
                action = ARCHIVE_PATTERN.sub( '', form['action'] )
                form['action'] = self.fix_netloc_port( action )
            except Exception as exc:
                self.logger.warning( exc )
