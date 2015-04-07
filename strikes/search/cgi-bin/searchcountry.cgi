#!/usr/bin/perl

print "Content-type:text/html\n\n";
use CGI;
my $q = new CGI;
my $query = $q->param("q");
my $alpha = $q->param("countrylist");
$query = $ARGV[0] if ($ARGV[0]);
$strict = 1;
#$alpha = $ARGV[1] if ($ARGV[1]);

$DEBUG = 0;

$dir = "/usr/local/apache2/alpha/cgi-bin";
open(file, "$dir/countries/countries.list.csv");
@countries = <file>;
close(file);

# {query:'amsterdam',results:[{"title":"Kraakbuurten Amsterdam: Nieuwmarkt, Waterlooplein, Burgwallen.","link":"http://search.socialhistory.org/Record/1191206","description":"Kraakbuurten Amsterdam: Nieuwmarkt, Waterlooplein, Burgwallen.","id":"1191206","category":"IISG"},
#{"title":"Kraakbuurten Amsterdam: Nieuwmarkt, Waterlooplein, Burgwallen.","link":"http://search.socialhistory.org/Record/1191142","description":"Kraakbuurten Amsterdam: Nieuwmarkt, Waterlooplein, Burgwallen.","id":"1191142","category":"IISG"},

$content.="{query:'$query',results:[";
foreach $str (@countries)
{
   $str=~s/\r|\n//g;
   my $true = 0;
   $true = 1 if ($str=~/$query/i);
   $true = 0 if ($alpha);

   if ($strict)
   {
	$true = 0;
	$true = 1 if ($str=~/^$query/i);
   }
   my $fletter;
    
   print "$str\n" if ($DEBUG);
   $id++;

   my $country;
   if ($id)
   {
	($country, $code) = split(/\;\;/, $str);
	if ($country=~/^(\S)/)
	{
	    $fletter = $1;
	}

	$alphabet{$fletter} = $fletter if ($fletter);
	$order{$fletter}{$country} = $country;
   };

   if ($true)
   {
 	my $squery = $country;
	$squery=~s/\s+/\+/g;
	$url = "https://www.google.nl/search?q=$squery&ie=utf-8&oe=utf-8&aq=t&rls=org.mozilla:en-US:official&client=firefox-a";
	$url = "/cgi-bin/wikiparser.cgi?q=$squery";
	$content.="{\"title\":\"$country\",\"link\":\"$url\",\"description\":\"$fletter\",\"id\":\"$id\",\"category\":\"IISG\"},\n";
   }
}
$content=~s/\,\s*$//g;
$content.="]}";

print "$content\n" unless ($alpha);

if ($alpha)
{

foreach $fletter (sort keys %alphabet)
{
     print "<p>$fletter </p>\n";
     my %countries = %{$order{$fletter}};

     foreach $country (sort keys %countries)
     {
	print "&nbsp;&nbsp;&nbsp;		<a href=# title=\"Country: $country\">$country</a> <br>\n";
     }

}
};
