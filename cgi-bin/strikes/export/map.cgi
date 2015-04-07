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
#print $q->header( "text/plain" );

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
$theme = "$Bin/../$dbconfig{theme}" if ($dbconfig{theme});

%locations = get_locations($dbh);
($template, $fieldshash, @tpl) = showtemplate($Bin, "$theme", "statplanet.csv");
@fields = @{$fieldshash} if ($fieldshash);
foreach $item (@tpl)
{
    $item=~s/\r//g;
    print "$item";
}

foreach $date (reverse sort keys %locations)
{
   my $active;
   my $thisline=",$date,";
   for ($k=1; $k<=$#fields; $k++)
   {
	$thisline.=",";
   }
   $thisline=~s/\,$//g;
   my %locs = %{$locations{$date}};
   my $yearline;
   # ,,Example data,,,strikes,,,,,,
   # ,,Example,,,,,,,,,42
   # ,,Example,,,,,,,,,26

   for ($k=0; $k<=1; $k++)
   {
       $yearline.=",";
   }
   $yearline.="Example,";
   for ($k=3; $k<=10; $k++)
   {
       $yearline.=",";
   }
   for ($k=11; $k<=$#fields; $k++)
   {
	$loc = $fields[$k];
	$value = $locs{$loc}; #.',' || ',';
	$yearline.="$value,";
	print "$date $loc $value\n" if ($DEBUG);
	$active++ if ($locs{$loc});
   }
   $yearline=~s/\,$//g;

   if ($active)
   {
       print "$thisline\n$yearline\n";
   };
}

sub showtemplate
{
    my ($Bin, $themedir, $templatename, $title, $datafile, $DEBUG) = @_;
    my $template;

    open(tpl, "$themedir/$templatename") || die "Can't open $themedir/$templatename\n";
    my @tpl = <tpl>;
    close(tpl);

    for ($i=0; $i<=$#tpl; $i++)
    {
	unless ($i)
	{
	    $header = $tpl[$i];
	    @fields = split(/\,/, $header);
	}

	$item = $tpl[$i];
        $item=~s/\%\%datafile\%\%/$datafile/g;
        $item=~s/\%\%title\%\%/$title/g;
        $item=~s/\%\%period\%\%/$period/g;
        $item=~s/\%\%refine\%\%/<b>$refine<\/b>/g;
        $item=~s/\%\%events\%\%/$eventstemplate/g;
        $item=~s/\%\%jsondata\%\%/$jsondatafile/g;
        $item=~s/\%\%thisyear\%\%/$custom_year/g;
        $item=~s/\%\%menu\%\%/$menu/g;
        $item=~s/\%\%chartdescription\%\%/$chartdescription/g;
        $item=~s/\%\%tsvdatafile\%\%/$tsvdatafile/g;
        $item=~s/\%\%csvdatafile\%\%/$csvdatafile/g;
        $item=~s/\%\%navigation_level1\%\%/$navigation_level1/g;
        $item=~s/\%\%navigation_level2\%\%/$navigation_level2/g;

        $custom_month = "-"."$custom_month" if ($custom_month);
        $item=~s/\%\%thismon\%\%/$custom_month/g;
        $item=~s/\%\%(\S+?\.js)\%\%/showtemplate($Bin, $1, $title, $datafile)/eg;
    }
    $template = "@tpl";

    return ($template, \@fields, @tpl);
}
