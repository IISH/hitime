#!/usr/bin/perl

#<tr><td>nl-NL</td><td>Dutch (Netherlands)</td></tr>

open(content, $ARGV[0]);
@content = <content>;
close(content);
$content = "@content";

$content=~s/\r|\n//gsxi;

my @items = split(/<tr>/, $content);
foreach $item (@items)
{
   print "$item\n";
   $item=~s/(<br\s+\/>|<p>|<\/p>)//gsxi;

   if ($item=~/^<td>(\S+?)<\/td><td>(.+?)\s+\((.+?)\)<\/td><\/tr>/i)
   {
	my ($code, $language, $country) = ($1, $2, $3);
	my $true = 1;
	$true = 0 if ($language=~/<img/i);

	if ($true)
	{
	    print "$language;;$country\n" if ($language); # && $country);
	};
   }
}
