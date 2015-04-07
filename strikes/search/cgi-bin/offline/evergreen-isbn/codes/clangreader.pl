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

   # <tr><td>en</td><td>English</td></tr>
   if ($item=~/^<td>(\S+?)<\/td><td>(.+?)<\/td><\/tr>/i)
   {
	my ($code, $language) = ($1, $2);
	my $true = 1;
	$true = 0 if ($item=~/\)/);

	if ($true)
	{
	    print "$code;;$language\n" if ($language); # && $country);
	};
   }
}
