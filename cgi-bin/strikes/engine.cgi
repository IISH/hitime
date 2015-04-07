#!/usr/bin/perl

use vars qw/$libpath/;
use FindBin qw($Bin);
BEGIN { $libpath="$Bin" };
use lib "$libpath";
use lib "$libpath/libs";

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

my ($menublocks, $varhash, %menu) = loadmenu("$Bin/conf/menu.conf");
%vars = %{$varhash} if ($varhash);

$env = "$ENV{REQUEST_URI}";
$custom_year = $q->param('year') || $ARGV[0];
$custom_month = $q->param('month') || $ARGV[1];
$custom_day = $q->param('day');
$varID = $q->param('varID') || $ARGV[2];
#$normalized = $q->param('norma') || $ARGV[3];
$logic = $q->param('logic') || $ARGV[4];
$fromyear = $q->param('fromyear');
$toyear = $q->param('toyear');
$publications = $q->param('pubvar');
$pubvar = $q->param('pubvar');
#$publications = "Year";
#$custom_year = $fromyear if ($fromyear);
#$varID = 5;

if ($varID)
{
   $varname = $vars{$varID};
   $chart = $menu{$varname}{datafile};
   $logic = $menu{$varname}{logic};
#   print "$chart\n";
}
$chart = "chart.defaultbar.tpl" unless ($chart);
$chartcolor = "#CC0000" if ($pubvar);
$uri = "pubvar=Month" if ($pubvar eq 'Year');
$uri = "pubvar=Day" if ($pubvar eq 'Month');

if ($env=~/yearfrom\=(\d+)/)
{
   $from = $1;
}

if ($env=~/yearto\=(\d+)/)
{
   $to = $1;
}

#print "$env $from $to\n";
$from = $q->param('fromyear');
$to = $q->param('toyear');

$| = 1;
my $year = $custom_year || $ARGV[0];
if ($env=~/\?year\=(\d+)/)
{
   $year = $1;
}
my $month = $custom_month || $ARGV[1];
my $day = $custom_day || $ARGV[2];
my $DEBUG = $ARGV[3];

#my %dbconfig = loadconfig("$Bin/quality.cfg");
my %dbconfig = loadconfig("$Bin/conf/strikes.conf");
my ($dbname, $dbhost, $dblogin, $dbpassword) = ($dbconfig{dbname}, $dbconfig{dbhost}, $dbconfig{dblogin}, $dbconfig{dbpassword});
my $dbh = DBI->connect("dbi:mysql:dbname=$dbname;host=$dbhost",$dblogin,$dbpassword,{AutoCommit=>1,RaiseError=>1,PrintError=>0});

%normalized = (1, "1", 6, "6", "7", "7", 8, "8", 9, 9, 10, 10, 11, 11, 12, 12);
if ($normalized) # && $normalized{$varID})
{
   my ($datahash, $aggrhash) = get_normalized_var($dbh, $year, $toyear, $varname, $variable);

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
#	   print "$date\t$data\n";
	}
   }
   exit(0);
}

if ($publications)
{
   ($datahash, $orderhash) = get_publications_stats($dbh, $publications, $custom_year, $custom_month, $fromyear, $toyear);
   %data = %{$datahash} if ($datahash);
   @order = @{$orderhash} if ($orderhash);
   foreach $var (@order) #sort keys %data)
   {
	$puboutput.="$var;;$data{$var}\n";
   }
}
#print "$from $to\n";
#$from = 1900;
#$to = 2000;
if (!$year)
{
   $output = events_by_years($dbh, $year, $from, $to);
};

if ($year && !$month)
{
    $originalorder++;
    $output = events_by_month($dbh, $year, $from, $to);
    ($cities, %cities) = get_cities($dbh, $year);
    $events = get_events($dbh, $year);

#    print "$output\n";
}
if ($year && $custom_month)
{
   $originalorder++;
   @weeks = build_month($custom_year, $custom_month);
   %count = events_by_days($dbh, $custom_year, $custom_month);
   foreach $week (@weeks)
   {
	$week=~s/\r|\n//g;
	my ($date, $dayname, $other) = split(/\;\;/, $week);
	if ($date=~/^(\d{4})\-(\d+)\-(\d+)/)
	{
	    my ($year, $mon, $day) = ($1, $2, $3);
	    $day=~s/^0//g;
	    $mon=~s/^0//g;
	    $daylegend = $id2month{$mon}."";
	    my $daycount = $count{$day} || '0';
	    $output.= "$day;;$daycount;;$daylegend;;$monthlegend;;$custom_month\n";
	}
   };
}

if ($varID) #$ && $go)
{
   $output = '';
   %values = get_values($dbh, $varname, $custom_year, $custom_month, 0, 0, $from, $to);
   foreach $name (sort keys %values)
   {
	$output.="$name;;$values{$name}\n";
   }

   #print "$varID $vars{$varID} $logic\n";
   if ($logic eq 'total')
   {
	print "date\tclose\n";
	$custom_year = $fromyear if ($fromyear);
	my ($datahash, $output) = get_value_for_timeline($dbh, $vars{$varID}, $custom_year, $toyear);
	%data = %{$datahash} if ($datahash);
	foreach $date (reverse sort keys %data)
	{
	   $xvalue=$data{$date};
	   $xvalue=~s/\,/\./g;
	   #$xvalue = int($xvalue);
	   print "$date\t$xvalue\n";
	}
	exit(0);
   }
}

if ($output)
{
   #  my ($Bin, $data, $ORIGINALORDER, $CUSTOM_XSTEP, $CUSTOM_YSTEP, $year, $month, $day, $cityhash, $DEBUG)
#   $custom_month = "05";
   $output = $puboutput if ($publications);
   #print "$chartcolor<br>";
   show_bar($uri, $chartcolor, $Bin, $orderhash, $chart, $output, $originalorder, 0, 0, $custom_year, $custom_month, $day, \%cities);
   #print "$output";
}

sub get_events
{
   my ($dbh, $year, $month, $day, $DEBUG) = @_;
   my $output;

   $sqlquery = "select ID, Jaar, Maand, Dag, Beroep, Plaats, Vakcentrale from main where 1=1";
   $sqlquery.=" and Jaar=$year" if ($year);

   my $sth = $dbh->prepare("$sqlquery");
   $sth->execute();

   while (my ($id, $thisyear, $thismonth, $thisday, $profession, $cities, $company) = $sth->fetchrow_array())
   {
	my $date;
	if ($thisyear && $thismonth && $thisday)
	{
	   $date = sprintf("%04d-%02d-%02d", $thisyear, $thismonth, $thisday);
	};
	$output.="$id;;$date;;$year;;$profession;;$cities;;$company\n";
   }

   return $output;
}

sub events_by_years
{
   my ($dbh, $year, $from, $to, $DEBUG) = @_;
   my $output;

   $sqlquery = "select count(*), JAAR from tblActies";
   $sqlquery.=" where JAAR >= $from and JAAR<=$to " if ($from && $to);
   $sqlquery.=" group by JAAR";
   my $sth = $dbh->prepare("$sqlquery");
   $sth->execute();

   while (my ($count, $year) = $sth->fetchrow_array())
   {
	$years{$year} = $count;
   }

   foreach $year (sort keys %years)
   {
	$output.= "$year;;$years{$year}\n";
   }

   return $output;
}

sub events_by_days
{
   my ($dbh, $year, $month) = @_;
   my ($output, %output);

   $sqlquery = "select count(*), DAG from tblActies where 1=1 and JAAR='$year' and MAAND='$month' group by DAG";
   my $sth = $dbh->prepare("$sqlquery");
   $sth->execute();
   while (my ($count, $day) = $sth->fetchrow_array())
   {
	$day=~s/^0//g;
        $val{$day} = $count;
   }

   return %val;
}

sub events_by_month
{
   my ($dbh, $year) = @_;
   my ($output, %output);

   my %month = (
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

   $sqlquery = "select count(*), MAAND from tblActies where 1=1 and JAAR='$year' group by MAAND";
   my $sth = $dbh->prepare("$sqlquery");
   $sth->execute();
   while (my ($count, $month) = $sth->fetchrow_array())
   {
        $val{$month} = $count;
   }

   foreach $month (sort keys %val)
   {
	$umonth = $month;
	$umonth=~s/^0//g;
	my $thismonth = $month{$umonth};
	#$thismonth = "0".$month if ($month > 0 && $month < 10);
	$thismonth = "Uknown" unless ($thismonth);
        $outputstr="$thismonth;;$val{$month}\n";
	$output{$outputstr} = $month;
   }

   foreach $str (sort {$output{$a} <=> $output{$b}} keys %output)
   {
	$output.="$str";
   }

   return $output;
}

sub get_cities 
{
   my ($dbh, $year, $month, $DEBUG) = @_;
   my ($output, %val, %output_by_months, %known);

   #$sqlquery = "select Plaats, count(*) from main where 1=1";
   $sqlquery = "select Plaats, Maand from main where 1=1 ";
   $sqlquery.=" and Jaar='$year'" if ($year); 
   $sqlquery.=" and Maand=$month" if ($month);
   #$sqlquery.=" group by Plaats";

   my $sth = $dbh->prepare("$sqlquery");
   $sth->execute();
   while (my ($city, $thismonth) = $sth->fetchrow_array())
   {
	$thismonth=~s/^0//g;
	$namemonth = $id2month{$thismonth} || $thismonth;
        $val{$city} = $namemonth;
	$output_by_months{$namemonth}.="$city\r" if (!$known{$year}{$city}{$thismonth} && $count_by_month{$namemonth} <= 10);
	$count_by_month{$namemonth}++;
	$known{$year}{$city}{$thismonth}++;
	print "$city $thismonth\n" if ($DEBUG);
   }

   return ($output, %output_by_months);
}

sub events_by_day_old
{
   my ($dbh, $year, $month) = @_;
   my $output;

   $sqlquery = "select count(*), DAG from tblActies where 1=1 and JAAR='$year' and MAAND='$month' group by DAG";
   my $sth = $dbh->prepare("$sqlquery");
   $sth->execute();
   while (my ($count, $day) = $sth->fetchrow_array())
   {
        $val{$day} = $count;
   }

   foreach $val (sort keys %val)
   {
        $output.="$val;;$val{$val}\n";
   }

   return $output;
}

sub actions_sort
{
   $sqlquery = "select * from tblActieSoort";
   my $sth = $dbh->prepare("$sqlquery");
   $sth->execute();

   while (my ($count, $action) = $sth->fetchrow_array())
   {

   }

   $sqlquery = "select count(*), ActieSoort from tblActies group by ActieSoort";
   my $sth = $dbh->prepare("$sqlquery");
   $sth->execute();

   while (my ($count, $action) = $sth->fetchrow_array())
   {

   }
}

sub loadconfig
{
    my ($configfile, $DEBUG) = @_;
    my %config;

    open(conf, $configfile);
    while (<conf>)
    {
        my $str = $_;
        $str=~s/\r|\n//g;
        my ($name, $value) = split(/\s*\=\s*/, $str);
        $config{$name} = $value;
    }
    close(conf);

    return %config;
}
