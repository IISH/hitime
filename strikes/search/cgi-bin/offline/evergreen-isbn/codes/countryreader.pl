#!/usr/bin/perl

#<tr>
#<td align="LEFT">ao</td>
#<td align="LEFT">Angola</td>
#</tr>

open(content, $ARGV[0]);
@content = <content>;
close(content);
$content = "@content";

$content=~s/\r|\n//gsxi;

my @items = split(/<tr>/, $content);
foreach $item (@items)
{
   if ($item=~/^\s*<td\s+align.+?>(\S+)<\/td>\s*<td.+?>(.+?)</i)
   {
	my ($code, $country) = ($1, $2);
	print "$code;;$country\n";
   }
}
