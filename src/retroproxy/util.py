
import re
import logging
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunsplit

ARCHIVE_PATTERN = re.compile(
    r'^((https?://web.archive.org)?/web/[0-9a-z_]*/)' )

def fix_netloc_port( url_in, url_port ):

    ''' Given a URL, insert the given listening port next to the host. '''

    nl_url = urlparse( url_in )
    if nl_url.netloc:
        netloc = nl_url.netloc + url_port
        return urlunsplit(
            (nl_url.scheme, netloc, nl_url.path,
            nl_url.query, nl_url.fragment) )

    else:
        return url_in

def process_html_links( text, url_port=80 ):

    logger = logging.getLogger( 'process.html.links' )

    soup = BeautifulSoup( text, 'html.parser' )
    for a in soup.findAll( 'a' ):
        try:
            a['href'] = ARCHIVE_PATTERN.sub( '', a['href'] )
    
            # Add our listening port to the netloc.
            a['href'] = fix_netloc_port( a['href'], url_port )
        except Exception as e:
            logger.warning( e )

    # Fix for static CSS.
    # TODO: Should these just be stripped?
    for link in soup.findAll( 'link' ):
        try:
            if link['href'].startswith( '/_static/' ):
                #link['href'] = \
                #    'https://web.archive.org{}'.format( link['href'] )
                link.extract()
        except Exception as e:
            logger.warning( e )

   # Fix for optional base tag.
    for base in soup.findAll( 'base' ):
        try:
            base['href'] = ARCHIVE_PATTERN.sub( '', base['href'] )

            base['href'] = fix_netloc_port( base['href'], url_port )
        except Exception as e:
            logger.warning( e )

    # Strip out archive modernity hacks.
    for script in soup.findAll( 'script', ):
        if 'src' in script.attrs and (
        'client-rewrite.js' in script.attrs['src'] or \
        'wbhack.js' in script.attrs['src'] ) or \
        'wbhack.' in script.text or \
        'WB_wombat_Init' in script.text:
            script.extract()

    return str( soup )

def process_html_imgs( text, url_port=80 ):

    logger = logging.getLogger( 'process.html.links' )

    soup = BeautifulSoup( text, 'html.parser' )

    # Fix for images relative to web.archive.org.
    #for img in soup.findAll( 'img' ):
    #    if img['src'].startswith( '/web/' ):
    #        img['src'] = 'https://web.archive.org{}'.format( img['src'] )

    # Fix for all images.
    for img in soup.findAll( 'img' ):
        try:
            img['src'] = ARCHIVE_PATTERN.sub( '', img['src'] )
            img['src'] = fix_netloc_port( img['src'], url_port )
        except Exception as e:
            logger.warning( e )

    return str( soup )
 
