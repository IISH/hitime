package Charts;

use vars qw(@ISA @EXPORT @EXPORT_OK %EXPORT_TAGS $VERSION);

use Exporter;

$VERSION = 1.00;
@ISA = qw(Exporter);

@EXPORT = qw(
		show_bar
		get_month_name
		loadmenu
            );

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

sub get_month_name
{
    my ($monthint, $DEBUG) = @_;

    $monthint=~s/^0//g;
    return $id2month{$monthint}; 
}

# Check use case
sub show_bar
{
    my ($uri, $chartcolor, $Bin, $orderhash, $chart, $data, $ORIGINALORDER, $CUSTOM_XSTEP, $CUSTOM_YSTEP, $custom_year, $custom_month, $custom_day, $cityhash, $DEBUG) = @_;
    my ($k, %cities, %legend, %real, %originalorder);

    %cities = %{$cityhash} if ($cityhash);
    @originalorder = @{$originalorder} if ($originalorder);

    my %month2id = reverse %id2month;
    #$DEBUG = 1;
    my $max = 100;
    $XSTEP = $CUSTOM_XSTEP || 5;
    $YSTEP = $CUSTOM_YSTEP || 100;
    $YMAX = 1000;

    $title = "'Chart'";
    $amountname = "'Amount'";

    my @data = split(/\n/sxi, $data);

    if ($chart) # eq 'bar')
    {
    $chart_default = $chart; # "bar_url.tpl";
    $chartname = $chart_default unless ($chartname);

    #while (my ($valueY, $valueX) = $sth->fetchrow_array())
    foreach $data (@data)
    {
	$data=~s/\r|\n//g;
	my ($valueX, $valueY, $legend, $real) = split(/\;\;/, $data);
	#print "$data $custom_month\n";
	#my $DEBUG = 1;
	print "DEBUG1 $valueX => $valueY\n" if ($DEBUG);
	$names{$valueY} = $valueX;
	$order{$valueX} = $valueX;
	$legend{$valueX} = $legend;
	$real{$valueX} = $real;
	$order{$valueX} = $k if ($ORIGINALORDER);
	$Yorder{$valueY} = $valueX;
	#$val{"$legend;;$valueX"} = $valueY;
	$val{$valueX} = $valueY;
	$legendval{"$legend;;$valueX"} = $valueY;
	$max = $valueY if ($max < $valueY);
	$k++;
    }

    my (@order, @backorder, $backorder);
    foreach $valueX (sort {$order{$a} <=> $order{$b}} keys %order)
    {
	push(@order, $valueX);
	#$backorder++ if ($order{$valueX}!~/June/);
    }

    foreach $key (sort {$legendval{$b} <=> $legendval{$a}} keys %legendval)
    {
	my ($thislegend, $thisvalue) = split(/\;\;/, $key);
        push(@backorder, $thisvalue);
	$backorder++ if ($key=~/(onbekend|werk|\/)/i);
    }

    @order = @backorder if ($backorder);
    foreach $valueX (@order)
    #foreach $valueX (sort {$order{$a} <=> $order{$b}} keys %order)
    {
	$valuesY.="$val{$valueX},";
	$valuesX.="\"$valueX\",";
	#$url = "/cgi-bin/strikes/engine.cgi";
	$url = "/cgi-bin/strikes/index.cgi";
        $url.="?year=$custom_year" if ($custom_year);
	my $thismon = $real{$valueX} || $valueX;
	my $thisday = $valueX;
	$thismon = "" if (!$custom_year);
	$thisday = "" if (!$custom_month);
	$thismon = $month2id{$thismon} if ($month2id{$thismon});

	unless ($custom_year)
	{
	   my $thisyear = $valueX;
	   my $thismon = $valueX;
	   $thisyear = $custom_year if ($custom_year);
	   $thismon = "" if (!$custom_month);
	   $thismon = $custom_month if ($custom_month);
	   
	   $url.="?year=$thisyear&month=$thismon";
	}
	$thismon = sprintf("%02d", $thismon) if ($thismon);
	$url.="&month=$thismon" if ($custom_year);
	$url.="&day=$thisday" if ($thisday);

	if ($custom_month) # && keys %cities)
	{
	   my %months = reverse %id2month;
	   my $month = $months{$valueX} || $valueX;
	   $month="0$month" if ($month < 10);
	   $month = '01' if ($month=~/Unknown/);
	   $url = "/strikes/timeline.$custom_year-$custom_month-$thisday";
	}
	$url.="&$uri" if ($uri);
	my $maintip;
	$tipvar = "strike records";
	$tipvar = "publications" if ($uri=~/pubvar/i);
	$maintip = "$val{$valueX} $tipvar\r$cities{$valueX}..." if ($cities{$valueX});
	$tip = $maintip || "$val{$valueX} $tipvar";
	$valuesXurl.="{\"top\":$val{$valueX},\"label\":\"Strike (#val#)\", \"tip\":\"$tip\",\"on-click\":\"$url\"},";

	# $valuesPie "value":6.5,"label":"hello (#val#)", "tip":"99 bottles of beer","on-click":"http://eden"
  	$valuesPie.="{\"value\":$val{$valueX},\"label\":\"$valueX\"},";
	$Xvalues.="{\"value\":$val{$valueX}},";

	# {"right":10},{"right":15},{"left":5,"right":15}
	$barvalues.="{\"left\": $val{$valueX}},";

	# {"value":9344,"label":"Expense"} for pies
	if ($valueX)
	{
	    my $value = $codes{$valueX} || $valueX;
	    $pievalues.="{\"value\":$val{$valueX},\"label\":\"$value\"},";
	};
    }
    $valuesY=~s/\,\s*$//g;
    $valuesX=~s/\,\s*$//g;
    $valuesPie=~s/\,\s*$//g;
    $pievalues=~s/\,\s*$//g;
    $Xvalues=~s/\,\s*$//g;
    $Xvalues=~s/\"\s+/\"/g;
    $barvalues=~s/\,\s*$//g;
    $barvalues=~s/\"\s+/\"/g;

    print "[DEBUG] $valuesX \n" if ($DEBUG);
    print "[DEBUG] $valuesY \n" if ($DEBUG);
    print "[DEBUG PIE] $pievalues\n" if ($DEBUG);
    showtemplate($chartcolor, $Bin, $chartname, $valuesY, $valuesX, $valuesPie, $valuesXurl, $Xvalues, $Yvalues, $barvalues);

    }

};

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

sub loadmenu
{
    my ($configfile, $DEBUG) = @_;
    my ($count, %config, %var);

    open(conf, $configfile);
    while (<conf>)
    {
        my $str = $_;
        $str=~s/\r|\n//g;

	#ReportID;;English Name;;Variable Name;;Description
        unless ($str=~/^\#/)
        {
            my ($id, $logic, $name, $var, $description, $chart, $datafile) = split(/\;\;/, $str);

	    if ($var)
	    {
	 	$count++;
		$id='0' unless ($id);
                $config{$var}{id} = $id;
		$config{$var}{name} = $name;
		$config{$var}{description} = $description;
		$config{$var}{logic} = $logic;
		$config{$var}{chart} = $chart || 'index.tpl';
		$config{$var}{datafile} = $datafile || 'chart.defaultbar.tpl';
		$var{$id} = $var;
	    }
        };
    }
    close(conf);

    return ($count, \%var, %config);
}

sub showtemplate
{
    my ($chartcolor, $Bin, $templatename, $names, $count, $valuesPie, $valueXurl, $Xvalues, $Yvalues, $barvalues, $DEBUG) = @_;
    my $template;

    open(tpl, "$Bin/templates/$templatename");
    my @tpl = <tpl>;
    close(tpl);

    @values = split(/\,/, $names);
    foreach $value (@values)
    {
	$value=~s/\"|\'//g;
	if ($MAX_Y < $value)
	{
	    $MAX_Y = $value;
	}
    }
    if ($MAX_Y > 1000)
    {
	$YSTEP = 5000;
    }
  
    if ($MAX_Y)
    {
	$max = $MAX_Y;
    }

    $max = int($max * 0.2) + $max;
    $max = 10 if ($max < 10);
    $max = 5 if ($max < 5);

    my @labels = split(/\,/, $count);
    if ($#labels < 90)
    {
	$XSTEP = 1;
    }
    if ($#labels >= 80)
    {
	$XSTEP = 9;
    }

    foreach $item (@labels)
    {
	$i++;
	$item=~s/\"//g;
	if ($i % $XSTEP == 0) # && $x)
	{
	   $newlabel.="\"$item\",";
	}
	else
	{
	   $newlabel.="\"\",";
	}
    }
    $newlabel=~s/\,\s*$//g;
    $count=$newlabel if ($newlabel);
    $chartcolor = "#587EB0" unless ($chartcolor);

    $valueXurl=~s/,$//g;
    foreach $item (@tpl)
    {
	$item=~s/\%\%labels\%\%/$count/g;
	$item=~s/\%\%values\%\%/$names/g;
	$item=~s/\%\%title\%\%/$title/g;
	$item=~s/\%\%amountname\%\%/$amountname/g;
	$item=~s/\%\%max\%\%/$max/g;
	$item=~s/\%\%ystep\%\%/$YSTEP/g;
	$item=~s/\%\%pievalues\%\%/$pievalues/g;
	$item=~s/\%\%valuesPie\%\%/$valuesPie/g;
	$item=~s/\%\%valueXurl\%\%/$valueXurl/g;
	$item=~s/\%\%Xvalues\%\%/$Xvalues/g;
	$item=~s/\%\%Yvalues\%\%/$Yvalues/g;
	$item=~s/\%\%barvalues\%\%/$barvalues/g;
	$item=~s/\%\%chartcolor\%\%/$chartcolor/g;
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

sub loadcodes
{
    my ($configfile, $DEBUG) = @_;
    my %names;

    open(conf, $configfile);
    while (<conf>)
    {
        my $str = $_;
	$str=~s/^\s+|\s+$//g;
        $str=~s/\r|\n//g;
	my ($code, $name) = split(/\s*\=\s*/, $str);
	$names{$code} = $name;
	print "$code => $name\n" if ($debug);
    }
    close(conf);

    return %names;
}
