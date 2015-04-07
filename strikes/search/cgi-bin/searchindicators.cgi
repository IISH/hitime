#!/usr/bin/perl

print "Content-type:text/html\n\n";
use CGI;
my $q = new CGI;
my $query = $q->param("q");
$query = $ARGV[0] if ($ARGV[0]);

$DEBUG = 0;

$dir = "/usr/local/apache2/alpha/cgi-bin";
open(file, "$dir/indicators/indicators/indicators.list.csv");
@countries = <file>;
close(file);

# {query:'amsterdam',results:[{"title":"Kraakbuurten Amsterdam: Nieuwmarkt, Waterlooplein, Burgwallen.","link":"http://search.socialhistory.org/Record/1191206","description":"Kraakbuurten Amsterdam: Nieuwmarkt, Waterlooplein, Burgwallen.","id":"1191206","category":"IISG"},
#{"title":"Kraakbuurten Amsterdam: Nieuwmarkt, Waterlooplein, Burgwallen.","link":"http://search.socialhistory.org/Record/1191142","description":"Kraakbuurten Amsterdam: Nieuwmarkt, Waterlooplein, Burgwallen.","id":"1191142","category":"IISG"},

$content.="{query:'$query',results:[";
foreach $str (@countries)
{
   $str=~s/\r|\n//g;
   my $found = 0;
   my @keywords = split(/\s+/, $query);

   foreach $key (@keywords)
   {
	if ($str=~/$key/i)
	{
	    $found++;
	}
   }

   if ($found)
   {
	print "$str\n" if ($DEBUG);
	$id++;
	my ($country, $code) = split(/\;\;/, $str);
 	my $squery = $country;
	$squery=~s/\s+/\+/g;
	$url = "https://www.google.nl/search?q=$squery&ie=utf-8&oe=utf-8&aq=t&rls=org.mozilla:en-US:official&client=firefox-a";
	$content{"{\"title\":\"$country\",\"link\":\"$url\",\"description\":\"$country\",\"id\":\"$id\",\"category\":\"Clio\"},\n"} = $found;
   }
}

foreach $str (sort {$content{$b} <=> $content{$a}} keys %content)
{
    $content.=$str;
};
$content=~s/\,\s*$//g;
$content.="]}";

print "$content\n";
