#!/usr/bin/perl

$file = "/var/www/strikes/testgraph.htm";
$file = "/usr/lib/cgi-bin/strikes/templates/linegraph.tpl";
open(file, $file);
@tpl = <file>;
close(file);

print "Content-type: text/html\n\n";
$template = "@tpl";

print $template;
