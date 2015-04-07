#!/usr/bin/perl

print "Content-type:text/html\n\n";
$query = $ARGV[0];
use CGI;
my $q = new CGI;
my $query = $q->param("q");
#$query = "kiev";

$query = "*%3A" unless ($query);
unless ($url)
{
    $url = "http://api.socialhistoryservices.org/solr/all/select/?q=$query"; #*&version=2.2&start=0&rows=0&facet=true&facet.field=$marcfield";
}

use LWP::Simple;
$result = get($url);
$result=~s/&lt;/</g;
$result=~s/&gt;/>/g;
$result=~s/<\/doc>/<\/doc>\n/g;

#print "$result\n";
$content = $result;
# tag="245"><marc:subfield code="a">
print "{query:'$query',results:[";
while ($content=~s/tag\="245">.+?code\=\"a\">(.+?)<.+?tag\=\"901\"><marc\:subfield\s+code\=\"a\">(\d+)<//xs)
{
     my ($name, $value) = ($1, $2);
     $name=~s/\"//g;
     $url = "http://search.socialhistory.org/Record/$value";
     # {query:'kansas',results:[{"title":"Kansas town","link":"Kansas town","description":"population: 260","id":"228","category":"Alabama"},
     #print "$name => $url\n";
     $str.= "{\"title\":\"$name\",\"link\":\"$url\",\"description\":\"$name\",\"id\":\"$value\",\"category\":\"IISG\"},\n";
};
$str=~s/\,$//gsxi;
#my $str;
print "$str]}";
