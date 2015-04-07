#!/usr/bin/perl

use CGI;
my $q = new CGI;

$DEBUG = 0;
#print $q->header( "text/html" );
$indicator = $q->param('indicator');
$topic = $q->param('topic');
$file = $q->param('file');

$templatedir = "/usr/local/apache2/alpha/cgi-bin/templates";

print "Content-type: text/html\n\n";

$maintpl = "$templatedir/map.sample.tpl";
open(tpl, "$maintpl");
@maphtml = <tpl>;
close(tpl);

$mapcontent = "@maphtml";

$true = 1;
if ($true && $topic && $indicator)
{
$dataset = "sample118.csv";
$dataset = "sample113.csv";
$dataset = "./tmp/$indicator.csv";
$convert = `/usr/local/bin/xls2csv -d utf-8 /usr/local/apache2/alpha/htdocs/excel/$topic/$indicator -c '|'|/usr/local/apache2/alpha/htdocs/map/analyzer.pl > /usr/local/apache2/alpha/htdocs/map/tmp/$indicator.csv`;
$makedos = `/usr/bin/todos /usr/local/apache2/alpha/htdocs/map/tmp/$indicator.csv`;
$topic = "Education".$topic;
}
my $root = "http://alpha.dev.clio-infra.eu/clioinfra/datasets";

if ($file && $true)
{
   $path = "/usr/local/apache2/alpha/htdocs/clioinfra/datasets";
   $file=~s/\.html//g;
   $path = "$path/$file";

   if ($file=~/^(.+?)\-\-(.+)$/)
   {
	$name = $1;
	$indicator = $2;
	$topic = $1;
	$indicator=~s/^\d+\s+//g;
   }

   $path=~s/\-\-/\//g;
   if (-e $path)
   {
        print "File: $path<br />\n" if ($DEBUG);
	my $tmpfile = $file;
	$tmpfile=~s/\W+//g;
	$tmpdir = "/usr/local/apache2/alpha/htdocs/map/tmp";
	#$convert = `/home/linuxadmin/clioinfra/bin/xlsx2csv.py -d '|' \"$path\"|/usr/local/apache2/alpha/htdocs/map/analyzer.pl > /usr/local/apache2/alpha/htdocs/map/tmp/$tmpfile.csv`;
	$convert1 = `/home/linuxadmin/clioinfra/bin/xlsx2csv.py -d '|' \"$path\" > $tmpdir/$tmpfile.csv.tmp`;
	$convert2 = `/usr/local/apache2/alpha/htdocs/map/analyzer.pl -csvfile '$tmpdir/$tmpfile.csv.tmp' -indicator '$indicator' -dataset '$dataset' -topic '$topic' -source 'Clio Infra' -link '$root/$topic/$indicator' -debug '$DEBUG' > $tmpdir/$tmpfile.csv`;

        if ($DEBUG)
	{
	     print "/usr/local/apache2/alpha/htdocs/map/analyzer.pl -csvfile '$tmpdir/$tmpfile.csv.tmp' -indicator '$indicator' -dataset '$dataset' -topic '$topic' -debug '$DEBUG' > $tmpdir/$tmpfile.csv\n";
	     print "<br />Convert $convert2\n";
	     exit(0);
	}
	print "OUTPUT: /usr/local/apache2/alpha/htdocs/map/tmp/$tmpfile.csv <br \>\n" if ($DEBUG);
	$makedos = `/usr/bin/todos /usr/local/apache2/alpha/htdocs/map/tmp/$tmpfile.csv`;	
	$dataset = "./tmp/$tmpfile.csv";
	#print "$convert\n";
   };

}

$mapcontent=~s/\%\%name\%\%/$indicator/gsxi;
$mapcontent=~s/\%\%dataset\%\%/$dataset/gsxi;
$mapcontent=~s/\%\%topic\%\%/$topic/gsix;

print "$mapcontent\n" unless ($DEBUG);
#
