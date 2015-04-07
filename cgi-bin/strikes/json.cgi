#!/usr/bin/perl

use vars qw/$libpath/;
use FindBin qw($Bin);
BEGIN { $libpath="$Bin" };
use lib "$libpath";
use lib "$libpath/libs";

require Encode;
use Unicode::Normalize;

use DB_File;
use DBI;

print "Content-type: text;\n\n";
use CGI;
my $q = new CGI;
$tag = $q->param('tag');
$value = $q->param('value');
$showurls = $q->param('showurls');
$period = $q->param('period');
$query = $q->param('q'); # || $ARGV[0];
$query=~s/\.html//sxig;
$filter_year = $q->param('year') || $ARGV[0];
$filter_month = $q->param('month') || $ARGV[1];
$filter_day = $q->param('day') || $ARGV[2];

if ($tag=~s/\$(\w+)//)
{
   $subfield = $1;
}

my $TXT = 1;
if ($showurls)
{
   $TXT = 0;
   $HTML = 1;
}
$| = 1;

my %dbconfig = loadconfig("$Bin/conf/strikes.conf");
my ($dbname, $dbhost, $dblogin, $dbpassword) = ($dbconfig{dbname}, $dbconfig{dbhost}, $dbconfig{dblogin}, $dbconfig{dbpassword});
my $dbh = DBI->connect("dbi:mysql:dbname=$dbname;host=$dbhost",$dblogin,$dbpassword,{AutoCommit=>1,RaiseError=>1,PrintError=>0});

print "Content-type: text\n\n" if ($HTML);

open(timeline, "$Bin/data.json");
@timeline = <timeline>;
close(timeline);

foreach $str (@timeline)
{
#   print "$str";
}

if ($dbh)
{
    $json = getrecords($dbh, $ids);

print <<"EOF";
{
    "timeline":
    {
        "headline":"Strikes Visual Timeline ",
        "type":"default",
                "text":"Strikes in Netherlands, from $period",
                "startDate":"2012,2,05",
        "date": [
		$json
		]
    }
}

EOF

};

sub getrecords
{
    my ($dbh, $ids, $DEBUG) = @_;

    #return unless ($ids);

    use LWP::Simple;
    my $sqlquery = "select id,year,ImageURL,FullDate,title,NewspaperTitle,text from DATAKB where 1=1";
    $sqlquery.=" and year='$filter_year'" if ($filter_year);
    $sqlquery.=" and month>='$filter_month'" if ($filter_month);
    $sqlquery.=" and day>='$filter_day'" if ($filter_day);
    $sqlquery.=" limit 100";
    my $sth = $dbh->prepare("$sqlquery");
    $sth->execute();
    #print "$ids\n";

    while (my ($id, $year, $img, $fulldate, $title, $newsTitle, $text) = $sth->fetchrow_array())
    {

	if ($img)
	{
	    $start = $fulldate || $year;
	    $start=~s/\-/\,/g; # 1963,8,9
	    $fullurl = $img;
	    $title=~s/\"|\'//g;
	    #$src= get($fullurl);
	    # src="http://imageviewer.kb.nl/ImagingService/imagingService?colour=89c5e7&coords=ddd:010464158:mpeg21:p001:alto&id=ddd:010464158:mpeg21:p001:image&r=0&s=0.1
	    # <a href="http://imageviewer.kb.nl/ImagingService/imagingService?id=ddd%3A010284888%3Ampeg21%3Ap011%3Aimage" class="icon icon_print" id="action_print"><span>Print</span></a>
	    #print "$src\n";
	    #http://kranten.kb.nl/view/article/id/ddd:010284888:mpeg21:p011:a0239 http://imageviewer.kb.nl/ImagingService/imagingService?id=ddd%3A010284888%3Ampeg21%3Ap011%3Aimage#image.jpg
	    if ($img=~/\/article\/id\/(\S+)$/sxi)
	    {
		$uID = $1;
		$uID=~s/\:/\%3A/g;
		$uID=~s/^(.+)\%3A\w+$/$1/g;
		$image = "http://imageviewer.kb.nl/ImagingService/imagingService?id=$uID"."%3Aimage";
		# %3Aa0239%3Aimage
	    }
	    $image.="#image.jpg";
	    #$image = "http://node-195.dev.socialhistoryservices.org/db/timeline/pic.jpg";
	    srand();
	    $hour = rand(24);
	    $time = int($hour);
	    $time = "0$time," if ($time < 10);
	    $start.=",$time,00,00";
	    $title = $newsTitle unless ($title);
	   
$json.="
            {
                \"startDate\":\"$start\",
                \"headline\":\"<a href=\'$img\'>$title</a>\",
                \"text\":\"$text $newsTitle<br /> <a href='$img' target='_blank'>$img</a>\",
                \"asset\":
                {
                    \"media\":\"$image\",
                    \"credit\":\"$id\",
                    \"caption\":\"$title\"
                }
            },
";
	}

#	print "<img src=\"$img\">\n";
	$count++;
    };

    print "$count records\n" if ($count && $DEBUG);
  
    $json=~s/\,$//gsxi;

    return $json;
};

sub remove_diacritics
{
    my ($str, $DEBUG) = @_;
   ##  convert to Unicode first
   ##  if your data comes in Latin-1, then uncomment:
   #$_ = Encode::decode( 'iso-8859-1', $_ );  

   $str=~s/\xe4/ae/g;  ##  treat characters ä ñ ö ü ÿ
   $str=~s/\xf1/ny/g;  ##  this was wrong in previous version of this doc    
   $str=~s/\xf6/oe/g;
   $str=~s/\xfc/ue/g;
   $str=~s/\xff/yu/g;

   $str = NFD( $str );   ##  decompose (Unicode Normalization Form D)
   $str=~s/\pM//g;         ##  strip combining characters

   # additional normalizations:

   $str=~s/\x{00df}/ss/g;  ##  German beta “ß” -> “ss”
   $str=~s/\x{00c6}/AE/g;  ##  Æ
   $str=~s/\x{00e6}/ae/g;  ##  æ
   $str=~s/\x{0132}/IJ/g;  ##  Ĳ
   $str=~s/\x{0133}/ij/g;  ##  ĳ
   $str=~s/\x{0152}/Oe/g;  ##  Œ
   $str=~s/\x{0153}/oe/g;  ##  œ

   $str=~tr/\x{00d0}\x{0110}\x{00f0}\x{0111}\x{0126}\x{0127}/DDddHh/; # ÐĐðđĦħ
   $str=~tr/\x{0131}\x{0138}\x{013f}\x{0141}\x{0140}\x{0142}/ikLLll/; # ıĸĿŁŀł
   $str=~tr/\x{014a}\x{0149}\x{014b}\x{00d8}\x{00f8}\x{017f}/NnnOos/; # ŊŉŋØøſ
   $str=~tr/\x{00de}\x{0166}\x{00fe}\x{0167}/TTtt/;                   # ÞŦþŧ

   $str=~s/[^\0-\x80]//g;  ##  clear everything else; optional

   return $str;
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
