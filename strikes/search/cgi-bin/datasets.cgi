#!/usr/bin/perl

print "Content-type: text/html\n\n";
$url = "http://data.un.org/DocumentData.aspx?id=265";
$content = `/usr/bin/wget -q \"$url\" -O -`;

$content=~s/^.+?ctl00_main_container.+?>//gsxi;
$content=~s/<div class="IconBar">.+$//gsxi;

print "Content-type: text/html\n\n";
use CGI;
my $q = new CGI;
my $query = $q->param("q");

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

