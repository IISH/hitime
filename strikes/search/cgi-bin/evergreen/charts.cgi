#!/usr/bin/perl

use vars qw/$libpath/;
use FindBin qw($Bin);
BEGIN { $libpath="$Bin" };
use lib "$libpath";
use lib "$libpath/lib";

use DBI;
use CGI;
my $q = new CGI;
my $material = $q->param("material");
my $month = $q->param("month");
my $insmonth = $q->param("insmonth");

my %dbconfig = loadconfig("$Bin/config/db.conf");
my ($dbname, $dbhost, $dblogin, $dbpassword) = ($dbconfig{dbname}, $dbconfig{dbhost}, $dbconfig{dblogin}, $dbconfig{dbpassword});
my $dbh = DBI->connect("dbi:Pg:dbname=$dbname;host=$dbhost",$dblogin,$dbpassword,{AutoCommit=>1,RaiseError=>1,PrintError=>0});

$usecase = $ARGV[0];
$conditions = $ARGV[1];
$title = "'Chart'";
$amountname = "'Amount'";

#if ($material || $month)
{
    print "Content-type: text/html\n\n";
    $usecase = $material if ($material);
    $usecase = "nam";
    $usecase = "nas";
    #$usecase = "npc";
    $conditions = $month if ($month);
    $conditions = "insmonth => $insmonth" if ($insmonth);
}

my $DEBUG = 1;
%queries = loadqueries("$Bin/config/usecases.conf");
$max = 100;

if ($usecase)
{
    usecase($dbh, $usecase, 0, %queries);
}

sub usecase
{
    my ($dbh, $usecase, $DEBUG, %queries) = @_;
    my ($valuesX, $valuesY);

    $sqlquery = $queries{$usecase};
    $conditions = "1=1" unless ($conditions);

    $insmonth = "201001";
    $conditions = "insmonth >= $insmonth" if ($insmonth);
    $conditions = "insmonth >= 201001 and insmonth <= 201205";
     $conditions = "insmonth >= 199502";
    $conditions = "insmonth >= 200601";
    $sqlquery=~s/\%\%conditions\%\%/$conditions/g;
    print "$sqlquery\n" if ($DEBUG);
    my $sth = $dbh->prepare("$sqlquery");
    $sth->execute();

    while (my ($valueY, $valueX) = $sth->fetchrow_array())
    {
	$names{$valueY} = $valueX;
	$order{$valueX} = $valueX;
	$val{$valueX} = $valueY;
	$max = $valueY if ($max < $valueY);
    }

    foreach $valueX (sort {$order{$a} <=> $order{$b}} keys %order)
    {
	$valuesY.="$val{$valueX},";
	$valuesX.="\"$valueX\",";
    }
    $valuesY=~s/\,\s*$//g;
    $valuesX=~s/\,\s*$//g;

    showtemplate("bar_1.tpl", $valuesY, $valuesX);

    print "$sqlquery\n" if ($DEBUG);
    exit(0);
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

        unless ($str=~/^\#/)
        {
            my ($name, $value) = split(/\s*\=\s*/, $str);
            $config{$name} = $value if ($value);
        };
    }
    close(conf);

    return %config;
}

sub showtemplate
{
    my ($templatename, $names, $count, $DEBUG) = @_;
    my $template;

    open(tpl, "$Bin/templates/$templatename");
    my @tpl = <tpl>;
    close(tpl);

    $max = int($max / 10) + $max;
    foreach $item (@tpl)
    {
	$item=~s/\%\%labels\%\%/$count/g;
	$item=~s/\%\%values\%\%/$names/g;
	$item=~s/\%\%title\%\%/$title/g;
	$item=~s/\%\%amountname\%\%/$amountname/g;
	$item=~s/\%\%max\%\%/$max/g;
    }
    $template = "@tpl";

print "$template\n";
    return $template;
};

sub loadqueries
{
    my ($configfile, $DEBUG) = @_;
    my %config;

    open(conf, $configfile);
    while (<conf>)
    {
        my $str = $_;
        $str=~s/\r|\n//g;

        unless ($str=~/^\#/)
        {
	    if ($str=~/^(.+?)\s*\|(.+)$/)
	    {
	  	my ($name, $value) = ($1, $2);
                $config{$name} = $value if ($value);
	    };
        };
    }
    close(conf);

    return %config;
}
