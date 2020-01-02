
function openWindow( caption, id=null, resizable=false, icoImg=null, x=0, y=0 ) {
    
    var winOuter = $('<div class="window-outer window-active"></div>');
    if( null != id ) {
        winOuter.attr( 'id', id );
    }
    $('#desktop').append( winOuter );

    var winInner = $('<div class="window-inner"><form class="window-form"></form></div>');
    $(winOuter).append( winInner );
    winOuter.draggable( {'handle': '.titlebar'} );
    if( resizable ) {
        winInner.resizable();
    }

    var titlebar = $('<div class="titlebar"><h1 class="titlebar-text">' + caption + '</h1></div>');
    $(winInner).prepend( titlebar );

    /* Add the window icon. */
    var icon = $('<div class="titlebar-icon"></div>');
    $(titlebar).prepend( icon );
    icon.css( 'background', 'url(' + staticPath + icoImg + 
        ') right ' + x.toString() + 'px bottom ' + y.toString() + 'px' );

    /* Add the window close button. */
    var btnClose = $('<button class="titlebar-close">X</button>');
    $(titlebar).append( btnClose );
    $(btnClose).click( function() {
        $(winOuter).remove();
    } );

    return winOuter;
}

function windowCreateInputText( win, label, value='', x='auto', y='auto' ) {

    /* Create a wrapper for the 3D chisel effect. */
    var wrapper = $('<div class="input-text-wrapper"></div>');
    var input = $('<input type="text" value="' + value + '" />');
    $(win).find( '.window-form' ).append( wrapper );
    $(wrapper).append( input );

    if( 'auto' != x ) {
        $(wrapper).css( 'left', x );
    }

    if( 'auto' != y ) {
        $(wrapper).css( 'top', y );
    }
}

function desktopCreateIcon( text, imgPath, imgX, imgY, x, y, callback ) {
    var icoImg = $('<div class="desktop-icon-img"></div>');

    var iconWrapper = $('<div class="desktop-icon"><div class="desktop-icon-overlay"></div>');
    iconWrapper.append( icoImg );

    icoImg.css( 'background', 'url(' + staticPath + imgPath + 
        ') right ' + imgX.toString() + 'px bottom ' + imgY.toString() + 'px' );

    var iconText = $('<div class="desktop-icon-text">' + text + '</div>');
    iconWrapper.append( iconText );

    $('#desktop').append( iconWrapper );

    $(iconWrapper).draggable( {'handle': '.desktop-icon-overlay' } );

    $(iconWrapper).click( function() {
        $('#desktop .desktop-icon').removeClass( 'desktop-icon-selected' );
        $(this).addClass( 'desktop-icon-selected' );
    } );
    $(iconWrapper).dblclick( callback );

    return iconWrapper;
}

$(document).ready( function() {
    //var win_foo = open_window( 'Foo', 'foo', true, 'icons-w95-16x16.png', 80, 272 );
    var ico_foo = desktopCreateIcon( "Foo", 'icons-w95-32x32.png', 800, 544, 10, 10, function() {
        /* Only open the window if it's not already open. */
        if( 0 >= $('#window-foo').length ) {
            var win_foo = openWindow( 'Foo', 'window-foo', true, 'icons-w95-16x16.png', 400, 272 );
            var input_txt = windowCreateInputText( win_foo, 'Date', '', '10px', '10px' );
        }
    } );
} );
