#!/usr/bin/perl 

use WWW::Mechanize;
use JSON -support_by_pp;

use vars qw/$libpath/;
use FindBin qw($Bin);
BEGIN { $libpath="$Bin" };
use lib "$libpath";
use lib "$libpath/../lib";
use lib "$libpath/../evergreen-quality/lib";

use lib '/usr/src/Evergreen-ILS-2.0.3/Open-ILS/src/perlmods';

use MARC::Record;
use MARC::File::XML (BinaryEncoding => 'UTF-8');
use MARC::Charset;
use OpenSRF::System;
use OpenILS::Utils::Fieldmapper;
use OpenSRF::Utils::SettingsClient;
use OpenSRF::EX qw/:try/;
use Encode;
use Unicode::Normalize;
use OpenILS::Application::AppUtils;
use OpenILS::Application::Cat::BibCommon;
use Quality;

MARC::Charset->assume_unicode(1);

my %phonecodes = loadcodes("$Bin/codes/country2code.csv");
my %marccodes = loadcodes("$Bin/codes/country2marc.csv");
my %codes = reverse %marccodes;
my %land2code = loadcodes("$Bin/codes/langcodes.csv");
my %lang2country = loadcodes("$Bin/codes/langcommon.csv");
my %marc2lang = loadcodes("$Bin/codes/lang2marc.csv");
my %lang2marc = reverse %marc2lang;

my ($start_id, $end_id);
my $bootstrap = '/openils/conf/opensrf_core.xml';

OpenSRF::System->bootstrap_client(config_file => $bootstrap);
Fieldmapper->import(IDL => OpenSRF::Utils::SettingsClient->new->config_value("IDL"));

# must be loaded and initialized after the IDL is parsed
use OpenILS::Utils::CStoreEditor;
OpenILS::Utils::CStoreEditor::init();

$logdir = "$Bin/logs";
mkdir $logdir unless (-e $logdir);

$templatedir = "$Bin/templates";
@template = loadtemplate("$templatedir/book.xml");
loadmapping("$templatedir/isbn.map");
$XML++;
my $DEBUG = 0;

$isbn = $ARGV[0]; # || "0596003722";
$isbn=~s/\"|\.|\-//g;
if ($isbn=~/^(\d{3})(\d)(\d{4})(\d{4})(\d)/)
{
    $barCODE = "$1-$2-$3-$4-$5";
}
else
{
    $barCODE = $isbn;
}

$url = "https://www.googleapis.com/books/v1/volumes?q=ISBN:$isbn&callback=handleResponse";
%bookset = fetch_json_page("$url");
$additional{"020\\|a"} = $isbn;
#exit(0) unless ($bookset{"volumeInfo|title"});

$MAKEMARC = 0;
if ($MAKEMARC)
{
    $marctemplate = "@template";
    foreach $item (sort keys %map)
    {
        if ($item=~/\$(.+)$/)
        {
            $mapvalue = $bookset{$1};

	    if ($XML)
	    {
	        my $tag = $map{$item}; # || '$1';
#	    my $DEBUG = 1;
	        print "<$tag>$mapvalue</$tag>\n" if ($DEBUG);
	        $tag=~s/\|/\\\|/g;
	        $marctemplate=~s/\%\%$tag\%\%/$mapvalue/gsx;
	    }
	    else
	    {
                print "$item [$1] => $mapvalue\n" if ($DEBUG);
	    };
        }
    }

    foreach $item (sort keys %additional)
    {
        $marctemplate=~s/\%\%$item\%\%/$additional{$item}/gsx;
    }

    $marctemplate=~s/\%\%\d+\|\w+\%\%//gsxi;
    print "$marctemplate\n";
}
else
{
    $marcxml = "  <leader>00620nam a22      a 4500</leader>\n<controlfield tag=\"008\">110701s                                d</controlfield>";
    my $record = MARC::Record->new();
    ## add the leader to the record 
    $record->leader('00620nam a22      a 4500');
    my $controlfield = MARC::Field->new( '008', '110701s                                d' );
    $record->insert_fields_ordered($controlfield);

    # Adding barcode
    if ($barCODE)
    {
	$mapvalue = $barCODE;
        my ($field, $subfield) = ("020", "a");
        my $newfield = MARC::Field->new($field,'','',$subfield => $mapvalue);
        $record->insert_fields_ordered($newfield);
    }


    $marctemplate = "@template";
    foreach $item (sort keys %map)
    {
	my ($country, $lang, $langcode);
        if ($item=~/\$(.+)$/)
        {
            $mapvalue = $bookset{$1};
	    my ($field, $subfield) = split(/\|/, $map{$item});

	    # Adding year
	    if ($field=~/260/i && $subfield=~/c/ && $mapvalue!~/\./)
	    {
		if ($mapvalue=~/^(\d{4})\-(\d{2})/)
		{
		   $mapvalue = $1;
		}

		$mapvalue.="." if ($mapvalue!~/\./);
	    }

	    # Adding pages
	    $mapvalue.=" p." if ($field=~/300/i && $subfield=~/a/ && $mapvalue!~/p\./);
	    my $true = 1;

	    # Adding country of origin
	    if ($field=~/044/i && $subfield=~/a/)
	    {
		my ($field, $subfield) = ("044", "a");
		$lang = lc $mapvalue;
		$country = $phonecodes{$lang};
		$countrycode = $codes{$country} || $lang;

                my $newfield = MARC::Field->new($field,'','',$subfield => $countrycode);
                $record->insert_fields_ordered($newfield);
		$true = 0;
	    } 

	    # Adding language
            if ($field=~/041/i && $subfield=~/a/)
            {
		my ($field, $subfield) = ("041", "a");
                $lang = lc $mapvalue;
                $language = $lang2country{$lang};
		$langcode = $lang2marc{$language} || $language || $lang;

                my $newfield = MARC::Field->new($field,'','',$subfield => $langcode);
                $record->insert_fields_ordered($newfield);
                $true = 0;
	    }

            # Adding language
            if ($field=~/245/i && $subfield=~/c/)
            {
		my ($field, $subfield) = ("100", "a");
	        my $newfield = MARC::Field->new($field,'','',$subfield => $mapvalue);
                $record->insert_fields_ordered($newfield);
	    }

	    if ($field && $true)
            {
                print "$item [$1] => $field $subfield $mapvalue\n" if ($DEBUG);
                my $newfield = MARC::Field->new($field,'','',$subfield => $mapvalue);
                $record->insert_fields_ordered($newfield);
            };
        }
    }

    $xml = $record->as_xml_record();
    my ($newxml, $changes) = fields_analyzer($xml);
    if ($changes)
    {
	$xml = $newxml;
	#print "After: $newxml\n";
    }

    print "$xml\n";

    #$SAVE++;
    if ($SAVE)
    {
        my $editor = OpenILS::Utils::CStoreEditor->new(xact=>1);
        my $record = OpenILS::Application::Cat::BibCommon->biblio_record_xml_import($editor, $xml); #, $source, $auto_tcn, 1, 1); 
        print "$record\n";
        $status = $editor->commit();
        print "$status\n";
    };
};

sub loadmapping
{
    my ($mapfile, $DEBUG) = @_;

    open(mapfile, $mapfile);
    @mapfile = <mapfile>;
    close(mapfile);

    foreach $item (@mapfile)
    {
        $item=~s/\r|\n//g;
        my ($from, $to) = split(/\;\;/, $item);

        $map{$from} = $to;
        #print "$from => $item\n";
    }

    return %map;
}

sub fetch_json_page
{
  my ($json_url, $DEBUG) = @_;
  my $browser = WWW::Mechanize->new();
  #$DEBUG = 1;

  eval{
    # download the json page:
    $browser->get( $json_url );
    my $content = $browser->content();
    $content=~s/\/\/\s*API\s*callback\n//gsxi;
    $content=~s/handleResponse\(\{\n//gsxi;
    $content=~s/\}\n\)\;$//gsxi;
    $content=~/^(.\"kind\".+)\{\s*\"kind.+$/gsxi;
    $content="{\n".$content."\n}";
    print "$content\n" if ($DEBUG);

    my $json = new JSON;
    
    # these are some nice json options to relax restrictions a bit:
    #use Encode;
    #$content = decode('iso-8859-1', $content);
    $json_text = $json->allow_nonref->utf8->relaxed->escape_slash->loose->allow_singlequote->allow_barekey->decode($content);

    foreach $book (@{$json_text->{items}}) {
	%entity = %{$book};
	foreach $key (sort keys %entity)
	{
	    if ($entity{$key}!~/(HASH|ARRAY)/)
	    {
	        print "\$bookset\{$key\} = $entity{$key}\n" if ($DEBUG);
	        $bookset{$book}{$key} = $entity{$key};
	    }
	    elsif($entity{$key}=~/HASH/)
	    {
		my %subhash = %{$entity{$key}};
		foreach $subkey (sort keys %subhash)
		{
		    if ($subhash{$subkey}!~/(HASH|ARRAY)/)
		    {
		        print "[D] $key|$subkey -> $subhash{$subkey}\n" if ($DEBUG);
		        $bookset{"$key|$subkey"} = $subhash{$subkey};
		    }
		    elsif ($subhash{$subkey}=~/HASH/)
	 	    {
			my %special = %{$subhash{$subkey}};
			foreach $spec (sort keys %special)
			{
			     print "[H] $key|$subkey|$spec -> $special{$spec}\n" if ($DEBUG);
			     $bookset{"$key|$subkey|$spec"} = $special{$spec};
		 	}	
	            }
		    elsif ($subhash{$subkey}=~/ARRAY/)
                    {
			my @array = @{$subhash{$subkey}};
			my $plainstr;
			foreach $string (@array)
			{
			    $plainstr.="$string, ";
			}
			$plainstr=~s/\,\s*$//g;

			print "[A] \$bookset\{$key\|$subkey\} = $plainstr\n" if ($DEBUG);
			$bookset{"$key|$subkey"} = $plainstr;
		    }
		}
	    }
	    elsif($entity{$key}=~/ARRAY/)
            {
		print "ARRAY $key\n" if ($DEBUG);
	    }
	}
	unless (keys %entity)
	{
	    print "ALone $book\n" if ($DEBUG);
	}
    }

  };
  # catch crashes:
  if($@){
    print "[[JSON ERROR]] JSON parser crashed! $@\n";
  }

    return %bookset;
}

sub loadtemplate
{
    my ($file, $DEBUG) = @_;
    my @template;

    open(file, $file);
    @template = <file>;
    close(file);

    return @template;
}

sub loadcodes
{
    my ($file, $DEBUG) = @_;
    my %codes;

    open(file, $file);
    my @codes = <file>;
    close(file);

    foreach $codeline (@codes)
    {
	$codeline=~s/\r|\n//g;
	my ($code, $country) = split(/\;\;/, $codeline);
	$codes{$code} = $country;
    }

    return %codes;
}
