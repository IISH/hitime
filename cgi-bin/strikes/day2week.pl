#!/usr/bin/perl 
use Data::Dump qw(dump);
use strict;
use warnings;
use Date::Day;

print "Enter the string: ";
my $str=<>;
chomp $str;

my @dates= split /; /,$str;

my %days = ("January",1,"February",2,"March",3,"April",4,"May",5,"June",6,"July",7,"August",8,"September",9,"October",10,"November",11,"December",12);

my @output = map {
    my @l = split/[ ,]+/;
    $l[0] = $days{$l[0]};
    [@l];
} @dates;

my @arr;
foreach my $date(@output) {
    print "@$date\n";
    push @arr, &day(@$date);
}
dump@arr;
