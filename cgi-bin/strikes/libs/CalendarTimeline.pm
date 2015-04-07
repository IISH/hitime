package CalendarTimeline;

use vars qw(@ISA @EXPORT @EXPORT_OK %EXPORT_TAGS $VERSION);

use Exporter;
use Time::Local;
use Date::Manip qw(UnixDate Date_SecsSince1970GMT);

$VERSION = 1.00;
@ISA = qw(Exporter);

@EXPORT = qw(
		build_month
            );

use Calendar::Simple;

sub build_month
{
   my ($thisyear, $thismonth, $DEBUG) = @_;
   my (@weeks);

   my @months = qw(January February March April May June July August
                  September October November December);
   my @week = qw(Su Mo Tu We Th Fr Sa);

   my $mon = $thismonth || (localtime)[4] + 1;
   my $yr  = $thisyear || (localtime)[5] + 1900;

   while ($yr < 1970)
   {
	$yr+=28;
   }
   my @month = calendar($mon, $yr);

   if ($DEBUG)
   {
      print "\n$months[$mon -1] $thisyear\n\n";
      print "Su Mo Tu We Th Fr Sa\n";

      foreach (@month) {
    	print map { $_ ? sprintf "%2d ", $_ : '   ' } @$_;
    	print "\n";
      }
   };

   foreach $week (@month)
   {
	my $i = 0;
	foreach $day (@{$week})
	{
	   my $fullday = sprintf("%04d-%02d-%02d;;%s", $thisyear, $thismonth, $day, $week[$i]);
	   if ($day)
	   {
		#eval { $timelocal = timegm( $sec, $min, $hour, $day, $thismonth, $thisyear); };
		my $timelocal;
		if ($day && $thismonth)
		{
		    eval { $timelocal = Date_SecsSince1970GMT($thismonth, $day, $thisyear, 0, 0, 0); };
		}
		push(@weeks, "$fullday;;$timelocal") if ($timelocal);
	        #print "$fullday\n" if ($day);
	   };
	   $i++;
	}
        #print "@{$day}\n";
   }

   return @weeks;
};
