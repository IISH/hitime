#!/usr/bin/perl

use vars qw/$libpath/;
use FindBin qw($Bin);
BEGIN { $libpath="$Bin" };
use lib "$libpath";
use lib "$libpath/libs";

use CGI;
use DBI;
use Engine;
use Charts;

my $q = new CGI;
print $q->header( "text/html" );
$year = $q->param('year');
$month = $q->param('month');
$day = $q->param('day');
$params = $q->param('params');

my %dbconfig = loadconfig("$Bin/conf/strikes.conf");
my ($dbname, $dbhost, $dblogin, $dbpassword) = ($dbconfig{dbname}, $dbconfig{dbhost}, $dbconfig{dblogin}, $dbconfig{dbpassword});
$theme = "$Bin/$dbconfig{theme}" if ($dbconfig{theme});
my $dbh = DBI->connect("dbi:mysql:dbname=$dbname;host=$dbhost",$dblogin,$dbpassword,{AutoCommit=>1,RaiseError=>1,PrintError=>0});

my ($menublocks, $varhash, %menu) = loadmenu("$Bin/conf/menu.conf");
%vars = %{$varhash} if ($varhash);
my $inblock = int($menublocks / 2);
unless ($year)
{
   $year = 1955;
}

if ($params=~/(\d{4})\-(\d{2})\-(\d{2})/)
{
   ($year, $month, $day) = ($1, $2, $3);
   $day = "01" unless ($day);
   $period = sprintf("%04d-%02d-%02d", $year, $month, $day);
}
elsif ($params=~/(\d{4})\-(\d{2})/)
{
   ($year, $month, $day) = ($1, $2, $3);
   $day = "01" unless ($day);
   $period = sprintf("%04d-%02d-%02d", $year, $month, $day);
}
elsif ($params=~/(\d{4})/)
{
   $year = $1;
}

#$month = "";
$jsonurl = "/cgi-bin/strikes/json_timeline.cgi?year=$year&month=$month&day=$day&period=$period&title=$title";
#print "$params $year $month $day\n";
$html = showtemplate($theme, "$Bin", "web.timeline.tmpl", $jsonurl, $title, $datafile);
print "$html\n";

sub showtemplate
{
    my ($theme, $Bin, $templatename, $jsonurl, $title, $datafile, $DEBUG) = @_;
    my $template;

    open(tpl, "$theme/$templatename");
    my @tpl = <tpl>;
    close(tpl);

    foreach $item (@tpl)
    {
        $item=~s/\%\%datafile\%\%/$datafile/g;
        $item=~s/\%\%title\%\%/$title/g;
        $item=~s/\%\%period\%\%/$period/g;
        $item=~s/\%\%refine\%\%/<b>$refine<\/b>/g;
	$item=~s/\%\%jsonurl\%\%/$jsonurl/g;
    }
    $template = "@tpl";

    return $template;
}
