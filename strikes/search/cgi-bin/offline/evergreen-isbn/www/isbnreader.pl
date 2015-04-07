#!/usr/bin/perl

use CGI;
my $q = new CGI;
print $q->header( "text/html" );
$isbn = $q->param('isbn');

unless ($isbn)
{
print <<"EOF";
<form action="/cgi-bin/offline/isbnreader.pl" method=get>
ISBN: <input type="text" name="isbn" value="" /><br />
<input type="submit" value="Get Details!">
</form>
EOF
}
else
{
#    print "ISBN: $isbn<br>";
    $marc = `/openils/applications/evergreen-isbn/isbnparser.pl '$isbn'`;
    $marc=~s/</\&lt\;/gsx;
    $marc=~s/>/\&gt\;/gsx;
    $marc=~s/\n/<br>/gsx;
    print "$marc\n";
}
