package Engine;

use vars qw(@ISA @EXPORT @EXPORT_OK %EXPORT_TAGS $VERSION);

use Exporter;

$VERSION = 1.00;
@ISA = qw(Exporter);

@EXPORT = qw(
		get_events
		events_by_years
		events_by_month
		loadconfig
		get_events_by_day
		get_values
		get_normalized_var
		get_value_for_timeline
		get_publications_stats
		get_locations
            );

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

sub get_locations
{
    my ($dbh, $year, $month, $limit, $DEBUG) = @_;
    my %locations;

    # Plaats | Gemeente | Kamervkoop | Provincie
    $sqlquery = "select id, Jaar, Maand, Dag, Plaats, Gemeente, Kamervkoop, Provincie from main";
#    $sqlquery.=" limit 100" if ($limit);

    my $sth = $dbh->prepare("$sqlquery");
    $sth->execute();

    while (my ($id, $year, $month, $day, $plaats, $gemeente, $kamervkoop, $provincie) = $sth->fetchrow_array())
    {
	my $date = $year;
	my $item = "$plaats // $gemeente // $kamervkoop // $provincie";
	$item.=" // Aa en Hunze";
	my @locations = split(/\s*\/\/\s*/, $item);
  	my %known;
	foreach $loc (@locations)
	{
	   $locations{$date}{$loc}++ unless ($known{$loc});
	   $known{$loc}++;
	};
    }

    return %locations;
}

sub get_publications_stats
{
    my ($dbh, $var, $year, $month, $fromyear, $toyear, $DEBUG) = @_;
    my (%data, %originalorder, @originalorder);

    $sqlquery = "select count(*) as c, $var from DATAKB where 1=1";
    $sqlquery.=" and Year=$year" if ($year);
    $sqlquery.=" and Month=$month" if ($month);
    $sqlquery.=" and Year>=$fromyear" if ($fromyear);
    $sqlquery.=" and Year<=$toyear" if ($toyear);
    $sqlquery.=" group by $var";

    my $sth = $dbh->prepare("$sqlquery");
    $sth->execute();

    while (my ($count, $variable) = $sth->fetchrow_array())
    {
	my $thisvar = $variable;
	if ($var=~/month/i)
  	{
	    $variable = $month{$variable} || $variable;
	}
	$data{$variable} = $count;
	$originalorder{$variable} = $thisvar;
    }

    foreach $var (sort {$originalorder{$a} <=> $originalorder{$b}} keys %originalorder)
    {
	push(@originalorder, $var);
    }

    return (\%data, \@originalorder);
}

sub get_value_for_timeline
{
   my ($dbh, $var, $year1, $year2, $indicator, $custom_variable) = @_;
   my (%data, %data2, $output, $notzero);

   $sqlquery = "select Jaar, Maand, Dag, $var from main where 1=1";
   $sqlquery.=" and Jaar=$year1" if ($year1 && !$year2);
   $sqlquery.=" and Jaar>=$year1 and Jaar<=$year2" if ($year1 && $year2);
   my $sth = $dbh->prepare("$sqlquery");
   #print "$sqlquery\n";
   $sth->execute();

   while (my ($year, $month, $day, $variable) = $sth->fetchrow_array())
   {
	$date = sprintf("%04d-%02d-%02d", $year, $month, $day);
	$output.="$date;;$variable\n" if ($month);
	$variable=~s/\,/\./g;
	$data{$date}+=$variable if ($month);
	$data2{$date}++;
	$notzero = 1 if ($variable > 0);
   }

   %data = %data2 unless ($notzero);
   return (\%data, $output);
}

sub get_normalized_var
{
   my ($dbh, $year1, $year2, $indicator, $custom_variable) = @_;
   my (%data, %aggr, %vardata);

   $sqlquery = "select distinct m.Jaar, m.Maand, m.Dag, s.nID, s.variable from $indicator"."_normalized as s, main as m where s.nID=m.id";
   $sqlquery.=" and m.Jaar>=$year1" if ($year1);
   $sqlquery.=" and m.Jaar<=$year2" if ($year2);
   $sqlquery.=" and s.variable='$custom_variable'" if ($custom_variable);

   my $sth = $dbh->prepare("$sqlquery");
   $sth->execute();

   while (my ($year, $month, $day, $id, $variable) = $sth->fetchrow_array())
   {
	my $date = sprintf("%04d-%02d-%02d", $year, $month, $day);
	$data{$date}{var} = $variable;
 	$data{$date}{id} = $id;
	$aggr{$date}{count}++;
	$aggr{$date}{var}{$variable}++;
	$vardata{$variable}{$date} = $id;
   }

   return (\%data, \%aggr, \%vardata);
}

sub get_values
{
   my ($dbh, $var, $year, $month, $day, $type, $from, $to, $DEBUG) = @_;
   my (%count, %stats);

   $sqlquery = "select count(*) as c, $var from main where 1=1";
   $sqlquery.=" and Jaar=$year" if ($year && !$to);
   $sqlquery.=" and Jaar>=$from and Jaar<=$to" if ($from && $to);
   $sqlquery.=" group by $var order by c desc";
   print "$sqlquery<br>" if ($DEBUG);

   my $sth = $dbh->prepare("$sqlquery");
   $sth->execute();

   while (my ($count, $name) = $sth->fetchrow_array())
   {
	$name=~s/\/\//\//g;
	$name=~s/^\s+|\s+$//g;
	$count=~s/^\s+|\s+$//g;
        $stats{$name} = $count;
   }

   return %stats;
}

sub get_events_by_day
{
   my ($dbh, $year, $month, $day, $type, $DEBUG) = @_;
   my (%count, %ids);

   $sqlquery = "select id, Jaar, Maand, Dag from main where 1=1 and Jaar in ($year) and Dag>0";
   my $sth = $dbh->prepare("$sqlquery");
   $sth->execute();

   while (my ($id, $thisyear, $thismon, $thisday) = $sth->fetchrow_array())
   {
 	my $thisdate = sprintf("%04d-%02d-%02d", $thisyear, $thismon, $thisday);
	unless ($type)
	{
	    $count{$thisdate}++;
	    $ids{$thisdate}.="$id, ";
	}
   }

   return %count;
}

sub get_events
{
   my ($dbh, $year, $month, $day, $eventID, $DEBUG) = @_;
   my ($output, %events);

   $sqlquery = "select ID, Jaar, Maand, Dag, Beroep, Plaats, Vakcentrale from main where 1=1";
   $sqlquery.=" and Jaar=$year" if ($year);
   $sqlquery.=" and Maand=$month" if ($month);
   $sqlquery.=" and ID=$eventID" if ($eventID);

   my $sth = $dbh->prepare("$sqlquery");
   $sth->execute();

   while (my ($id, $thisyear, $thismonth, $thisday, $profession, $cities, $company) = $sth->fetchrow_array())
   {
	my ($date, $order);
	if ($thisyear && $thismonth && $thisday)
	{
	   $date = sprintf("%04d-%02d-%02d", $thisyear, $thismonth, $thisday);
	   $order = $date;
	};
        if (!$date && $thisyear && $thismonth)
        {
           $date = sprintf("%04d-%02d", $thisyear, $thismonth);
	   $order = $date."00";
        };

	my $key="$id;;$date;;$year;;$profession;;$cities;;$company\n";
	$output.="$key";
	$order=~s/\D+//g;
	$order = "$year"."9999" unless ($order);
	$events{$key} = $order;
	$ids.="$id, ";
   }

   $ids=~s/\,\s+$//g;
   %stats = get_kb_stats($dbh, $ids);

   return (\%events, \%stats);
}

sub get_kb_stats
{
   my ($dbh, $ids, $year, $month, $day, $DEBUG) = @_;
   my %stats;

   $sqlquery = "select count(*), id from DATAKB where id in ($ids) group by id";
   my $sth = $dbh->prepare("$sqlquery");
   $sth->execute();

   while (my ($count, $id) = $sth->fetchrow_array())
   {
	$stats{$id} = $count;
   }

   return %stats;
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

sub events_by_day
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
