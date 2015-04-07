#!/usr/bin/perl

use vars qw/$libpath/;
use FindBin qw($Bin);
BEGIN { $libpath="$Bin" };
use lib "$libpath";
use lib "$libpath/../lib";
use Text::Similarity::Overlaps;
#my %options = ('normalize' => 1, 'verbose' => 1);
my %options = ('normalize' => 1);
my $mod = Text::Similarity::Overlaps->new (\%options);

open(file, "$Bin/search.tmpl");
@html = <file>;
close(file);

# Modules
use DBI;
use CGI;
use URI;

print "Content-type: text/html\n\n" unless ($ARGV[1]);

$| = 1;

my %dbconfig = loadconfig("$Bin/../conf/auth.config");
my ($dbname, $dbhost, $dblogin, $dbpassword) = ($dbconfig{dbname}, $dbconfig{dbhost}, $dbconfig{dblogin}, $dbconfig{dbpassword});
my $dbh = DBI->connect("dbi:mysql:dbname=$dbname;host=$dbhost",$dblogin,$dbpassword,{AutoCommit=>1,RaiseError=>1,PrintError=>0});

use Sphinx::Search;
my $qr = new CGI();
my $uri = URI->new($qr->url(-rewrite=>1, -path=>1));

my $path = $ENV{REQUEST_URI}; 
$path=~s/\/api\/\?//g;
my $q = new CGI("$path"); 
my $HTML = 1;
$HTML = '' if ($ARGV[1]);

# Input parameters
$query = $q->param('query') || $ARGV[0];
$searchtext = $q->param('text') || $ARGV[1];
$query=~s/\_/ /g;
$searchtext=~s/\_/ /g;
$charset = $q->param('charset');
$url = $q->param('url');

# Access parameters
$username = $q->param("username");

# Control parameters
$country = $q->param("country");
$limit = $q->param("MaxRows");
$DEBUG = $q->param('debug');

$api = $q->param('api');
$param = $q->param('param');
#$DEBUG++;

# Output parameters
$html = $q->param('html');
$project = $q->param('project');
$project = "general" unless ($project);
$grouplimit = $q->param("grouplimit");
$link2evergreen = $q->param("link");

# Advanced parameters
$createNERmodel = $q->param("createNERmodel");
$score = $q->param("score");
$score = 0.4 unless ($score);

$HTML++ if ($searchtext);
$br = "<br>" if ($HTML);
#showsearchform() if ($HTML && ($query || $searchtext));
print "$br" if ($HTML);

#print "$searchtext\n";
if (!$query && !$searchtext)
{
   $searchtext = $ARGV[1];
}
$page = $q->param('page');
$limit = $q->param('limit');
$blocktitle = $q->param('blocktitle');
#showhtml($query, @html) unless ($api);

%MARC21 = ("100a", "P", "110a", "C", "111a", "M", "130a", "U", "148a", "Ch", "150a", "T", "151a", "Geo", "155a", "Gen"); 
%MARC21full = ("100a", "Personal Name", "110a", "Corporate Name", "111a", "Meeting Name", "130a", "Uniform Title", "148a", "Chronological Term", "150a", "Topic Term", "151a", "Geographic Name", "155a", "Genre/Form Term");
%HiTIME = ("100a", "PERS", "110a", "ORG", "111a", "ORG", "130a", "ORG", "148a", "TERM", "150a", "TERM", "151a", "LOC", "155a", "TERM");

unless ($query)
{
    $query = $input{query} || $ARGV[0];
}

my $sphinx = Sphinx::Search->new();     # Вызываем конструктор
$sphinx->SetServer( '127.0.0.1', 9300); #localhost', 3312 );
$limit = 10 if ($api && !$limit);
$limit = 20000 unless ($limit);
$offset = 0;

if ($page)
{
    $offset = (($page - 1) * $limit);
}
$sphinx->SetLimits($offset, $limit);

#$sphinx->SetLimits($offset, $limit);
print "$sphinx\n" if ($DEBUG eq 'sphinx');
print 'Connected... '.$sphinx->_Connect() if ($DEBUG eq 'sphinx');

my $text = $query;

if ($searchtext)
{
   print "$searchtext\n" if ($DEBUG);
   text_processor($query, $searchtext, $DEBUG);
}

if ($query)
{
   my ($id, $author) = single_query_search($query, '', $DEBUG, 'verbose');
   print "$query $id $author\n";
}

if (!$query && !$searchtext)
{
    $content = `/bin/cat /var/www/api/index.html`;
    print "$content\n" if (!$ARGV[1]);
}

sub text_processor
{
    my ($item, $fulltext, $DEBUG) = @_;
    my %candidates;

    #print "<br />";
    my @tmpsentences = split(/(\.|\!|\?)\s+/sxi, $fulltext); 
    foreach $text (@tmpsentences)
    {
	$tID++;
	if ($text=~/\w+/)
	{
	    #print "[DEBUG] $tID $text<br/>";
	    push(@sentences, $text);
	};
    }

    my @sentences;
    my $tmptext = $fulltext;
    while ($tmptext=~s/^(.+?\S{2,}(\.|\?|\!))//sxi)
    {
	$string = $1;
	$stringID++;
	print "[DEBUG] $stringID $string\n<br>" if ($DEBUG);
	push(@sentences, $string);
    }
    push(@sentences, $tmptext) if ($tmptext);

    #foreach $text (@sentences)
    for ($stringID=0; $stringID<=$#sentences; $stringID++)
    {
	my $text = $sentences[$stringID];
	my $original = $text;
	my (@chains, %lexicon, $lexchain, $newtext, @coordinates, $keyID, %candidates);
	my @words = split(/[^\w]/, $text);
	foreach $keyword (@words)
	{
	    $keyID++;
	    my $up;
	    if ($keyword=~/^[A-Z]/)
	    {
		$up++;
		$candidates{$keyword}++;
	    }

	    if ($up)
	    {
	        #$newtext.="$keyword($up) ";
		$newtext.="$keyword ";
		$coordinates[$keyID] = 1;
	    }
	    else
	    {
		$newtext.="$keyword ";
		$coordinates[$keyID] = 0;
	    }

	    if ($keyword=~/\b(\d{4})\b/)
	    {
		$dates{$1} = $1;
	    }

	    $lexicon{UP}{$keyID} = $up;
	    $lexicon{id}{$keyID} = $keyID;
	    $lexicon{words}{$keyID} = $keyword;
	    my $lineID = $stringID + 1;
	    $pos{$lineID}{$keyID} = $keyword;
	    $lexicon{positions}{$keyword}{$keyID} = $keyID;
	    $tokenizer{$lineID}{$keyword} = $keyID;
	    print "Tokenize [$lineID][$keyID] $keyword <br>\n" if ($DEBUG);
	}

	my %IDs = %{$lexicon{id}};
	my $IDline;
	foreach $id (sort {$IDs{$a} <=> $IDs{$b}} keys %IDs)
	{
	    $IDline.="$id($lexicon{UP}{$id}) ";
	}
# 	print "$IDline\n";

	$STEP = 3;
	for ($i=1; $i<=$#coordinates; $i++)
	{
	   my ($status, $lexchain, $showchain, $lexIDs, %filter);
	   if ($coordinates[$i])
	   {

	   for ($j=$i; $j<=$i+$STEP; $j++)
	   {
		print "		J$j=$coordinates[$j]-$lexicon{UP}{$j}) " if ($DEBUG);
		$showchain.="$j($lexicon{words}{$j}-$lexicon{UP}{$j})-";
		if (length($lexicon{words}{$j}) > 2)
		{
		    $lexchain.="$lexicon{words}{$j} ";
		    $lexIDs.="$j-";
		    $status++ if ($coordinates[$j]);
		};
		$filter{$showchain} = $lexicon{UP}{$i};
	   }
	   $lexchain=~s/\-$//g;

	   my $proceed = 'ok';
	   $proceed = 0 if ($status <= 1 and $filter{$showchain} <= 1);
	   if ($proceed) # > 2)
	   {
		#print "[$status] $showchain => $lexchain Filter: $filter{$showchain} <br>\n";
		$lexchain=~s/(\bthe\b|\bor\b|\band\b|\bwas\b|\bwere\b|\bfor\b)//gsxi;
		$IDcoords{$lexchain} = $lexIDs;
		$lines{$lexchain} = $stringID + 1;
		push(@chains, $lexchain);
	   }

	   $block++;
	   }
	   
	   #print "\nI$i $coordinates[$i]\n";
	}

	foreach $text (sort keys %candidates)
	{
	   if (length($text) > 1)
	   {
	     my ($id, $author, $rank, $typehash, $typeamount) = single_query_search($text, '', $DEBUG);
	     my %thistypes = %{$typehash};
	     my ($typeselected, %typestats, $max);
	     foreach $type (sort keys %thistypes)
	     {
		#print "$type $thistypes{$type} <BR>";
		if (!$max || ($thistypes{$type} > $max))
		{
		   $typeselected = $type;
		   $max = $thistypes{$type};
		}
	     }

	     #my $#thiswords = split(/\s+/, $text);
	
	     my $lineID = $stringID + 1;
	     # Find start and end word
	     my @simplewords = split(/\s+/, $text);
	     my ($start, $end);
	     for ($sID=0; $sID<=$#simplewords; $sID++)
	     {
		my $token = $simplewords[$sID];
		$start = $tokenizer{$lineID}{$token} unless ($start);	
		$end = $tokenizer{$lineID}{$token};	
	     }
	     print "$text;;$author;;$id;;$lineID;;$start;;$end;;$MARC21full{$typeselected} <br>\n";
	   }
	} 

	$linked++;
	foreach $text (@chains)
	{
	    my $origtext = $text;
	    my ($id, $author, $rank, $typehash, $typeamount) = single_query_search($text, '', $DEBUG);
	    $mode = "<font color=\"blue\">Exact Match</font>";
	    unless ($author)
	    {
		($id, $author, $rank, $typehash, $typeamount) = single_query_search('', $text, $DEBUG);
		$mode = "<font color=\"red\">Fuzzy Match</font>";
	    }
	    my $url = "<a href=\"http://search.socialhistory.org/Search/Results?lookfor=$author&type=AllFields\">$author</a>";

	    my ($typeprediction, $selectedtype);
	    if ($typehash)
	    {
		%types = %{$typehash} if ($typehash);
	        foreach $type (sort {$types{$b} <=> $types{$a}} keys %types)
	        {
		    my $score = sprintf("%.2f", ($types{$type} / $typeamount * 100));
		    my $types = $types{$type};
		    $typeprediction.="<a href=\"http://www.loc.gov/marc/authority/ad1xx3xx.html\" title=\"$MARC21full{$type}\">$type</a>:$score% ";
		    $selectedtype = "$MARC21full{$type}";
	  	}
	    }

	    if ($id && $rank > $score)
	    {
		my $showrank = int($rank * 100);
		$text=~s/^\s+|\s+$//g;
             
		my @simplewords = split(/\s+/, $text);
                my ($start, $end);
		my $lineID = $lines{$origtext};
                for ($sID=0; $sID<=$#simplewords; $sID++)
                {
                    my $token = $simplewords[$sID];
                    $start = $tokenizer{$lineID}{$token} unless ($start);
                    $end = $tokenizer{$lineID}{$token};
                }
		print "$text;;$text;;$id;;$lineID;;$start;;$end;;$selectedtype $br\n";
	        #print "<b>$showrank%</b> $mode $text => $url ID=$id <br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Disambiguation: $typeprediction $br\n"; # $IDcoords{$text} $br\n";
	    };
	}
    }

    foreach $date (sort keys %dates)
    {
	print "$date;;;;;;Year <br>\n" if ($showdates);
    }
}

sub single_query_search
{
    my ($item, $text, $DEBUG, $showtype) = @_;
    my (%results, $results, $authID, $author, $query, %rank, $amount);

    $DEBUG = 1 if ($showtype eq 'verbose');
    #print "Entities Matching for $item <br>\n" if ($DEBUG);

    $index = "hitimeauth";
    @types = ("100a", "110a");
    # ->SetFilter('type', \@types)
    if ($item)
    {
       %weights=(name=>3, annotation=>1);
	$query = $item;
       #$results = $sphinx->SetMatchMode(SPH_MATCH_ANY)     # Режим поиска совпадений
        $results = $sphinx->SetMatchMode(SPH_MATCH_EXTENDED)
                      ->SetSortMode(SPH_SORT_RELEVANCE) # Режим сортировки
                      ->SetFieldWeights(\%weights)      # Вес полей
                      ->Query($item, $index);      # Поисковый запрос

       $found=$results->{total_found};
       $attrs=$results->{words};
       my $err = $sphinx->GetLastError;
    };

    if ($text)
    {
	$query = $text;
       %weights=(name=>3, annotation=>1);
       $results = $sphinx->SetMatchMode(SPH_MATCH_ANY)     # Режим поиска совпадений
                      ->SetSortMode(SPH_SORT_RELEVANCE) # Режим сортировки
                      ->SetFieldWeights(\%weights)      # Вес полей
                      ->Query($text, $index);      # Поисковый запрос

       $found=$results->{total_found};
       $attrs=$results->{words};
       my $err = $sphinx->GetLastError;
    }

    $limit = $found;
    $length = 100000;
    my %types;
    for (my $x=0; $x<$limit; $x++)
    {
	%main = %{$results->{matches}->[$x]};
	foreach $key (sort keys %main)
	{
#	   print "I $key => $main{$key}\n";
	}

        $url = $results->{matches}->[$x]->{url};
	$entity = $results->{matches}->[$x]->{entity};
	$id = $results->{matches}->[$x]->{doc};
	$type = $results->{matches}->[$x]->{type};
	%info = %{$results->{matches}->[$x]};
	$i++;
	$rating{$doc} = $i;
	#unless ($authID)

	my $score = $mod->getSimilarityStrings($entity, $query);
	$rank{$entity} = $score;
	#print "$entity $type <br>\n";
	$IDs{$entity} = $id;
	$types{$type}++ if ($type);
	$amount++ if ($type);

	if (length($entity) > 2 && length($entity) < $length)
	{
	   $authID = $id;
	   $author = $entity;
	   $length = length($entity);
	}

	print "$item;;$entity;;$id;;$MARC21full{$type} $br\n" if ($DEBUG);

        if ($doc)
        {
            print "$x id => $doc\n" if ($DEBUG);
            $ids.="$doc, ";
        };

    }

    my ($authID, $author, $mainscore, $minlen); 
    foreach $entity (sort {$rank{$b} <=> $rank{$a}} keys %rank)
    {
	#print "$entity $IDs{$entity}<br>\n" if ($DEBUG);
	$mainscore = $rank{$entity} unless ($mainscore);
	$len = length($entity);

	if ($rank{$entity} >= $mainscore && (!$minlen || $len <= $minlen))
	{
	   $authID = $IDs{$entity};
	   $author = $entity;	
	   $minlen = $len;
	};
    }

    return ($authID, $author, $rank{$author}, \%types, $amount);
}

sub showpages
{
    my ($pages, $html, $DEBUG) = @_;

    #print "$html<p>Pages:&nbsp;";
    $pages = 50 if ($pages > 50);
    $page = 1 unless ($page);
    for ($i=1; $i<=$pages; $i++)
    {
	unless ($i eq $page)
	{
	print "<a href=/cgi-bin/search.cgi?query=$query&page=$i>$i</a>&nbsp;";
	}
	else
	{
	    print "<b>$i</b>&nbsp;";
	}
    }
}

sub finder
{
    my ($dbh, $content, $DEBUG) = @_;
    my $output;

    my @words = split(/\s+/, $content);

    my $sqlwords;
    for ($i=0; $i<=$#words; $i++)
    {
	$word = $words[$i];
	$word=~s/[\,\.\?\!]//g;
	$tokens{$word} = $i;

	if ($word=~/[A-Z]/)
	{
	    $wordtoken = $dbh->quote($word);
	    $sqlwords.="$wordtoken, ";
	};
    }

    if ($sqlwords)
    {
	$sqlwords=~s/\,\s+$//g;
	$sqlquery = "select entity, type, amount from names where entity in ($sqlwords)";
	print "$sqlquery\n"; # if ($DEBUG);
        my $sth = $dbh->prepare("$sqlquery");
        $sth->execute();

        while (my ($token, $type, $amount) = $sth->fetchrow_array())
        {
	     #$output.="$token/$type ";
	     $class{$token} = "$token/$type";
	}
    }

    for ($i=0; $i<=$#words; $i++)
    {
        $word = $words[$i];
	$tmpword = $word;
	$tmpword=~s/[\,\.\?\!]//g;
	my $wordout = $class{$tmpword} || "$word/O";
	$output.="$wordout ";  
    }

    $output=~s/^\s+|\s+$//g;
    print "$output\n";

    return;
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

# select * from authorities where entity like '%Schmier%' limit 10;

sub showhtml
{
    my ($query, @html) = @_;

    foreach $item (@html)
    {
	$item=~s/\%\%query\%\%/$query/gi;
	print "$item\n";
    }
}

sub showsearchform
{
print <<"EOF";
<center>
<table>

<tbody><tr>
<td width="7%"> </td>

<td colspan="2" width="86%"> </td>
<td width="7%"> &nbsp;&nbsp; </td>

</tr>

<tr>
<td width="7%"> </td>
<td colspan="2" border="0" align="left" valign="top" width="86%">

<a href="http://ilk.uvt.nl/hitime/"><img src="http://ilk.uvt.nl/hitime/HiTiME_web_title.png" alt="HiTiME: Historical Timeline Mining and Extraction" border="0"></a>

</td>
<td width="7%"> </td>

</tr>
</table>
</center>
<center>
<p>
<form action="/cgi-bin/auth.search.cgi" method=get>
<TEXTAREA NAME="text" COLS=100 ROWS=6>$searchtext</TEXTAREA>
<input type="submit" value="Analyse!">
</form>
</p>
</center>
EOF

}


