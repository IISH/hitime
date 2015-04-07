#!/usr/bin/perl

use vars qw/$libpath/;
use FindBin qw($Bin);
BEGIN { $libpath="$Bin" };
use lib "$libpath";
use lib "$libpath/../libs";

use DBI;
use Charts;
use Engine;
use CGI;
use CalendarTimeline;

my %id2month = (
   1, "January",
   2, "February",
   3, "March",
   4, "April",
   5, "May",
   6, "June",
   7, "July",
   8, "August",
   9, "September",
   10, "October",
   11, "November",
   12, "December",
   0, "Unknown"
);

my $q = new CGI;
print $q->header( "text/plain" );

$custom_year = $q->param('year');
$custom_month = $q->param('month');
$custom_day = $q->param('day');
$from = $q->param('fromyear');
$to = $q->param('toyear');
$varID = $q->param('varID');
$pubvar = $q->param('pubvar');

my ($menublocks, $varhash, %menu) = loadmenu("$Bin/../conf/menu.conf");
%vars = %{$varhash} if ($varhash);

my %dbconfig = loadconfig("$Bin/../conf/strikes.conf");
my ($dbname, $dbhost, $dblogin, $dbpassword) = ($dbconfig{dbname}, $dbconfig{dbhost}, $dbconfig{dblogin}, $dbconfig{dbpassword});
my $dbh = DBI->connect("dbi:mysql:dbname=$dbname;host=$dbhost",$dblogin,$dbpassword,{AutoCommit=>1,RaiseError=>1,PrintError=>0});

#$varname = "Bedrijf";
#$varname = "Eisen";

$varname = $vars{$varID};
$logic = $menu{$varname}{logic};
if (!$year && !$to)
{
   $year = 1900;
   $toyear = 2000;
}

#if ($normalized) # && $normalized{$varID})
if ($varname)
{
   $year = $from if ($from && !$year);
   my ($datahash, $aggrhash, $vardatahash) = get_normalized_var($dbh, $year, $to, $varname, $variable);

   dataout($vardatahash);
}

sub dataout
{
   my ($datahash, $DEBUG) = @_;
   my %data = %{$datahash} if ($datahash);
  
   #print "var,date,count\n";
   print "symbol,date,price\n";
   foreach $var (sort keys %data)
   {
	my %dates = %{$data{$var}};
	my (%count, %order);
	foreach $date (sort keys %dates)
	{
	    $var=~s/\"|\,/ /g;
	    $var=~s/^\s+|\s+$//g;
	    if ($date=~/^(\d+)\-(\d+)/)
	    {
		my ($y, $m) = ($1, $2);
		$m=~s/^0//g;
		my $mon = $id2month{$m};
		if ($mon=~/^(\S{3})/)
		{
		  $mon = $1;
		}

		if ($mon ne 'Unk')
		{
		   $count{"$mon $y"}++;
		   $order{"$mon $y"} = "$y$m";
		};
	    }
	    #print "\"$var\",$date,1\n";
	}
	
	my $active = 0;
	$active = 1 if ($varcount < 50);
	print "$var,Jan 1900,0\n" if ($active);
	foreach $date (sort {$order{$a} <=> $order{$b}} keys %order)
	{
	    print "$var,$date,$count{$date}\n" if ($active); # if ($var=~/Onb/);
	}
	print "$var,Jan 2000,0\n" if ($active);
	$varcount++;
   }
}

sub aggregation
{
   my ($aggrhash, $DEBUG) = @_;
   %aggr = %{$aggrhash} if ($aggrhash);

   print "date\tclose\n";
   foreach $date (reverse sort keys %aggr)
   {
        %data = %{$aggr{$date}{count}};
        my $count = $aggr{$date}{count};
        if ($date=~/^(\d+)\-(\d+)\-(\d+)/)
        {
           my ($year, $mon, $day) = ($1, $2, $3);
           $year=~s/^20//g;
           $mon=~s/^0//g;
           my $montext = $id2month{$mon};
           if ($montext=~/^(\w{3})/)
           {
                $umon = $1;
           }
           $udate = "$day-$umon-$year";
        }
        print "$date\t$count\n";
        foreach $data (sort keys %data)
        {
#          print "$date\t$data\n";
        }
   }
   exit(0);
}
