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
#   print "$item\n";
   $item=~s/(<br\s+\/>|<p>|<\/p>)//gsxi;

   # <td class="code">tum</td> <td>Tumbuka</td> </tr>
   if ($item=~/^\s*<td.+?>(\S+?)<\/td>\s*<td>(.+?)<\/td>\s*<\/tr>/i)
   {
	my ($code, $language) = ($1, $2, $3);
	my $true = 1;

	if ($true)
	{
	    print "$code;;$language\n" if ($language); # && $country);
	};
   }
}
