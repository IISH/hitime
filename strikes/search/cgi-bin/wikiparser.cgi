#!/usr/bin/perl


use LWP::Simple;

print "Content-type: text/html\n\n";
use CGI;
my $q = new CGI;
my $query = $q->param("q");

$url = "http://en.wikipedia.org/wiki/$query";
$content = `/usr/bin/wget \"$url\" -O -`;

$content=~s/^.+?(<h1\s+id="firstHeading".+)$/$1/gsxi;
$content=~s/^(.+)<span.+?See\_also\">See\s+also.+$/$1/gsxi;


open(template, "/usr/local/apache2/alpha/cgi-bin/wiki/template.tpl");
@content = <template>;
close(template);
foreach $str (@content)
{
   $str=~s/\%\%content\%\%/$content/g;
   push(@result, $str);
}

$content = "@result";
print "$content\n";
