#!/usr/bin/perl

use vars qw/$libpath/;
use FindBin qw($Bin);
BEGIN { $libpath="$Bin" };
use lib "$libpath";
use lib "$libpath/../";

use CalendarTimeline;

for ($i=1; $i<=12; $i++)
#$i = 6;
{
   $year = $ARGV[0];
   $month = $i || $ARGV[1] - 1;
   @weeks = build_month($year, $month);

   foreach $day (@weeks)
   {
	print "$day\n";
   }
}
