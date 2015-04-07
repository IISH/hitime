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

my %dbconfig = loadconfig("$Bin/conf/strikes.conf");
my ($dbname, $dbhost, $dblogin, $dbpassword) = ($dbconfig{dbname}, $dbconfig{dbhost}, $dbconfig{dblogin}, $dbconfig{dbpassword});
$theme = "$Bin/$dbconfig{theme}" if ($dbconfig{theme});
my $dbh = DBI->connect("dbi:mysql:dbname=$dbname;host=$dbhost",$dblogin,$dbpassword,{AutoCommit=>1,RaiseError=>1,PrintError=>0});

my ($menublocks, $varhash, %menu) = loadmenu("$Bin/conf/menu.conf");
%vars = %{$varhash} if ($varhash);
my $inblock = int($menublocks / 2);

my $q = new CGI;
print "Content-type: text/html\n\n";

$custom_year = $q->param('year');
$custom_month = $q->param('month');
$custom_day = $q->param('day');
$from = $q->param('fromyear');
$to = $q->param('toyear');
$varID = $q->param('varID');
$showMAP = 'yes' if ($varID == 13);
$pubvar = $q->param('pubvar');
$timeline = $q->param('timeline');
$to=~s/Present/2100/g;
$params = $q->param('params');

$datafile = "/cgi-bin/strikes/engine.cgi";
$show_from = $custom_year || $from;
$navigation_level1 = "Visualization:&nbsp;<a href=\"/cgi-bin/strikes/index.cgi\">Charts</a>&nbsp;<a href=\"/strikes/map/geo.$from-$to\">Maps</a>&nbsp;<a href=\"/strikes/timeline.$show_from\">Timelines</a>&nbsp;";
$navigation_level2 = "Data Source:&nbsp;<a href=\"/cgi-bin/strikes/index.cgi\">Strikes</a>&nbsp;<a href=\"/cgi-bin/strikes/index.cgi\">Publications</a>&nbsp;<a href=\"/cgi-bin/strikes/index.cgi\">All</a>";

if ($timeline)
{
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

}

$selectedcolor = "background-color:#efefef;";
$datafile.="?"; # if ($from);
if ($custom_year)
{
   $addparam.="year=$custom_year&month=$custom_month";
   $datafile.="$addparam";
}
if ($vars{$varID})
{
   $datafile.="&varID=$varID";
}
if ($pubvar)
{
   $datafile.="&pubvar=$pubvar";
}
$datafile.="&fromyear=$from" if ($from);
$addparam="&fromyear=$from" if ($from);
$datafile.="&toyear=$to" if ($to);
$addparam.="&toyear=$to" if ($to);
$datafile.="&xccxcx=10";

use LWP::Simple;
$dataurl = "http://localhost".$datafile;
#print "$dataurl<br>";
$content = `/usr/bin/wget -q \"$dataurl\" -O - `;
#$content = "$datafile";
my $indexurl = "/cgi-bin/strikes/index.cgi";

$defaultsource{pubvar} = $selectedcolor if ($pubvar);
$defaultchart{map} = $selectedcolor if ($showMAP);
$defaultchart{chart} = $selectedcolor unless (keys %defaultchart);
$defaultsource{chart} = $selectedcolor unless (keys %defaultsource);

$mapurl = "/strikes/map/geo";
$mapurl.= ".$custom_year" if ($custom_year);
#$mapurl.= ".$from-$to" if ($from && $to);
$mapurl.=".2010";
$navigation_level1 = "
<div style=\"float:left;width:100px;border:1px solid;text-align:center;$defaultchart{chart}\"><a href=\"$indexurl?$addparam\">Charts</a></div>
<div style=\"float:left;width:100px;border:1px solid;text-align:center;$defaultchart{map}\"><a href=\"/strikes/map/geo.$from-$to\" target=\"_blank\">Map</a></div>
<div style=\"float:left;width:100px;border:1px solid;text-align:center;\"><a href=\"/strikes/timeline.$show_from\" target=\"_blank\">Timeline</a></div>
";

$navigation_level2 = "
<div style=\"float:left;width:100px;border:1px solid;text-align:center;$defaultsource{chart}\"><a href=\"$indexurl?$addparam\">Strikes</a></div>
<div style=\"float:left;width:100px;border:1px solid;text-align:center;$defaultsource{pubvar}\"><a href=\"$indexurl?$addparam&pubvar=Year\">Publications</a></div>
";

unless ($varID)
{
$navigation_level2.="
<div style=\"float:left;width:100px;border:1px solid;text-align:center;\"><a href=\"$indexurl\?$addparam&compare=Year\">Compare</a></div>
";
}

my @time = (localtime)[0..5];
my $updatedate = sprintf("%04d-%02d-%02d_%02d%02d%02d", $time[5]+1900, $time[4]+1, $time[3], $time[2], $time[1], $time[0]);

$varname = $vars{$varID};
$logic = $menu{$varname}{logic};
$fileout = "/var/www/strikes/tmp/$data".$updatedate.".csv";
$jsondatafile = "/cgi-bin/strikes/json_timeline.cgi?year=$custom_year";
$tsvdatafile = "/cgi-bin/strikes/engine.cgi?year=$custom_year&varID=$varID&logic=".$logic."&pubvar=".$pubvar;
$csvdatafile = "/cgi-bin/strikes/export/csv.cgi?year=$custom_year&varID=$varID&fromyear=$from&toyear=$to";
if ($from || $to)
{
   $tsvdatafile.="&fromyear=$from&toyear=$to";
}

foreach $var (sort keys %menu)
{
   $thisblock++;
   my $thisurl = "$indexurl?";
   $thisurl.="&fromyear=$from" if ($from);
   $thisurl.="&toyear=$to" if ($to);
   $thisurl.="&year=$custom_year" if ($custom_year);
   $thisurl.="&month=$custom_month" if ($custom_month);
   my $thisID = $menu{$var}{id};
   my $thisname = $menu{$var}{description};
   my $thischar = $menu{$var}{chart};
   my $engname = $menu{$var}{name};
   $thisurl.="&varID=$thisID";
   if ($engname)
   {
       if ($thisID != $varID)
       {
   	  $menu.="<a href\=\"$thisurl\" title=\"$thisname\">$engname</a>&nbsp;\n" if ($engname!~/^map/i);
       }
       else
       {
	  $menu.="<b>$engname</b>&nbsp;\n" if ($engname!~/^map/i);
	  $chartdescription = "<br>$thisname";
	  $maintemplate = $thischar;
       }
   };
   $menu.="<br>\n" if ($thisblock eq $inblock);
   $vars{$thisID} = $var;
}

$menu = "<p>Publications from <a href=\"http://www.kb.nl\" target=_blank>National Library of the Netherlands</a></p>" if ($pubvar);

$chartdescription = "<br />How many News Stories about Strikes have been published" if ($pubvar);
$chartdescription.=", ".get_month_name($custom_month) if (get_month_name($custom_month));
$chartdescription.=", $custom_year" if ($custom_year);
$chartdescription.=", $from - $to" if ($from && $to);
if ($pubvar)
{
    $chartdescription = "$chartdescription, from Royal Library";
}
else
{
    $chartdescription = "$chartdescription, from Strikes Database";
}

open(file, ">$fileout");
print file "$content";
close(file);
$datafile = $fileout;
$datafile=~s/^.+?(\/strikes)/$1/g;
#print "X $content\n";
#print "$datafile\n";
#print "$ENV{REQUEST_URI}\n";

$title = "Strikes in Netherlands";
if ($custom_year && $custom_month)
{
   $title.=", ".get_month_name($custom_month).", $custom_year";
}
elsif ($custom_year)
{
   $title.=", $custom_year";
}

$todate = $to;
$todate = "Present" if ($to > 2000);
$period = "Timeline from $from to $todate" if ($from || $to);

$default = 1 if (!$year && !$from && !$to); 
#$period = "Complete Timeline" if ($default);
#if ($default)
$menuscript = "$indexurl?varID=$varID";
{
    $STEP = 100;
    $refine = "<li>Period</li>\n";
    for ($i= 1500; $i<=2013; $i++)
    {
	if ($i % $STEP == 0)
	{
	    my ($from, $to) = ($i, $i+$STEP);
	    $to = "Present" if ($to > 2000);
	    $cell = 10;
	    $cell = "15" if ($to eq "Present");
	    $refine.="<li><a href=\"$menuscript&fromyear=$from&toyear=$to\">&nbsp;$from - $to&nbsp;</a></li>\n";
	    #print "$i $\n";
	}
    }
    $refine.="<li><a href=\"$indexurl\">Full Scope</a></li>\n";
}

$template = "index.tpl";
$template = "index.tpl" if ($custom_year);
$template = "index.month.tpl" if ($custom_month);

$template = "linegraph.tpl" if ($logic eq 'total');
$template = "linegraph.tpl" if ($custom_year && $logic eq 'total');
$template = $maintemplate if ($maintemplate); #"tracking.tpl" if ($varID eq 7);
$template = "timeline.tpl" if ($timeline);
$template = "new.timeline.tmpl" if ($timeline);
#print "$template\n$logic\n$tsvdatafile\n";

#$template = "index.timeline.tpl" if ($custom_year);
if ($custom_year && $custom_month)
{
   my ($eventshash, $counthash) = get_events($dbh, $custom_year, $custom_month);
   %events = %{$eventshash} if ($eventshash);
   %count = %{$counthash} if ($counthash);
   $eventstemplate ="<div><table width=100%><tr height=15><td></td></tr>\n<tr bgcolor=#efefef><td align=right>Date</td><td width=5></td><td>Profession of strikers</td><td>Locations</td><td width=10% align=center>Publications</td></tr>";
   foreach $key (sort {$events{$a} <=> $events{$b}} keys %events)
   {
	$key=~s/\/\//\, /g;
	$key=~s/\,\s+$//g;
	my ($id, $date, $Uyear, $prof, $city, $details) = split(/\;\;/, $key);
	if ($prof=~/^(\w)(.+)$/)
	{
	   $prof = uc($1).$2;
	}
	my $url = "http://www2.iisg.nl/databases/stakingen/details.asp?id=$id";
	$date = $Uyear unless ($date);
	$amount = $count{$id} || '0';
	$eventstemplate.="<tr><td align=right>$date</td><td width=5></td><td><a href=\"$url\" title=\"$city\" target=_blank>$prof</td><td>$city</td><td align=center>$amount</td></tr>";
   }
   $eventstemplate.="</div></table>";
};
$content = showtemplate($Bin, $template, $title, $datafile);
my @content = split(/\n/, $content);
foreach $str (@content)
{
   $str=~s/^\s+|\s+$//g;
   print "$str\n";
}

sub showtemplate
{
    my ($Bin, $templatename, $title, $datafile, $DEBUG) = @_;
    my $template;

    open(tpl, "$theme/$templatename");
    my @tpl = <tpl>;
    close(tpl);

    $chartdescription = "<b><font color=#000000>$chartdescription</font></b>";
    foreach $item (@tpl)
    {
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
	$item=~s/\%\%jsonurl\%\%/$jsonurl/g;
	
	$custom_month = "-"."$custom_month" if ($custom_month);
	$item=~s/\%\%thismon\%\%/$custom_month/g;
	$item=~s/\%\%(\S+?\.js)\%\%/showtemplate($Bin, $1, $title, $datafile)/eg;
    }
    $template = "@tpl";

    return $template;
}
