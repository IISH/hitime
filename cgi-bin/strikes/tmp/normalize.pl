#!/usr/bin/perl

$str = "Sector, Voornamelijk, Beroep, Bond, Bedrijf, Eisen, Uitkomst, Karakter, Bedrijf";

my @tables = split(/\,\s+/, $str);

foreach $name (@tables)
{
$table = $name."_normalized";
$index = $name."index";
$varindex = $name."varindex";

print <<"EOF";
DROP TABLE IF EXISTS $table;
CREATE TABLE $table
(
   nID bigint,
   variable varchar(255) 
);
CREATE INDEX $index on $table(nID);
CREATE INDEX $varindex on $table(variable);
EOF
}
