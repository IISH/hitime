#!/usr/bin/perl

use vars qw/$libpath/;
use FindBin qw($Bin);
BEGIN { $libpath="$Bin" };
use lib "$libpath/../";
use lib "$libpath/../libs";

use CGI;
use DBI;
use Engine;
use Charts;

my %dbconfig = loadconfig("$Bin/../conf/strikes.conf");
my ($dbname, $dbhost, $dblogin, $dbpassword) = ($dbconfig{dbname}, $dbconfig{dbhost}, $dbconfig{dblogin}, $dbconfig{dbpassword});
my $dbh = DBI->connect("dbi:mysql:dbname=$dbname;host=$dbhost",$dblogin,$dbpassword,{AutoCommit=>1,RaiseError=>1,PrintError=>0});

$sqlquery = "select id, Sector, Voornamelijk, Beroep, Bond, Bedrijf, Eisen, Uitkomst, Karakter, Bedrijf from main"; # where Jaar>=2000 and Jaar<=2005 limit 10;";
$names = $sqlquery;
$names=~s/select\s+//g;
$names=~s/\s+from\s+.+$//g;
@names = split(/\,\s+/, $names);
print "@names\n";
my $sth = $dbh->prepare("$sqlquery");
$sth->execute();

#while (my ($id, $Sector, $Voornamelijk, $Beroep, $Bond, $Bedrijf, $Eisen, $Uitkomst, $Karakter, $Bedrijf) = $sth->fetchrow_array())
while (my (@items) = $sth->fetchrow_array())
{
   $id = $items[0];
   for ($i=1; $i<=$#items; $i++)
   {
	my @values = split(/\/\//, $items[$i]);
	$table = $names[$i]."_normalized";
	foreach $value (@values)
	{
	    $sqlvalue = $dbh->quote($value);
	    $sql = "INSERT INTO $table (nID, variable) values ('$id', $sqlvalue);";
	    $dbh->do("$sql");
      	    #print "$i $id $names[$i] @value\n";
	};
   };
}
