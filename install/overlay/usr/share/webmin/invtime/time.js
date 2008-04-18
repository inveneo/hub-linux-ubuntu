var secs, mins, hours;

function timeInit() {
    secs  = document.forms[1].second;
    mins  = document.forms[1].minute;
    hours = document.forms[1].hour;
}

function timeUpdate() {
    s = parseInt(secs.selectedIndex);
    s = s ? s : 0;
    s = s + 5;
    if( s > 59 ) {
        s -= 60;
        m = parseInt(mins.selectedIndex);
        m= m ? m : 0;
        m += 1;
        if( m > 59 ) {
            m -= 60;
            h = parseInt(hours.selectedIndex);
            h = h ? h : 0;
            h += 1;
            if( h > 23 ) {
                h -= 24;
            }
            hours.selectedIndex = h;
        }
        mins.selectedIndex = m;
    }
    secs.selectedIndex = s;
    setTimeout('timeUpdate()', 5000);
}

function packNum(t) {
    return (t < 10 ? '0'+t : t);
}
