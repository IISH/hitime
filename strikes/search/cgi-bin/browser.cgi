#!/usr/bin/perl

$topicID = $ARGV[0];
$exceldir = $topicID;

print "Content-type: text/html\n\n";
$id = 4;
$topicID = "/usr/local/apache2/alpha/htdocs/excel/$id/";
open(list, "$topicID/description.txt");
@list = <list>;
close(list);

$content = "<table>\n";
$content.= "<tr style=\"background-color:#A6C603\"><td><b>Indicator Name</b></td><td>Excel</td><td>Visualize</td></tr>\n";
foreach $str (@list)
{
    $str=~s/\r|\n//g;
    # SE.SEC.ENRL.FE.ZS;;"Secondary education, pupils (% female)";;SE.SEC.ENRL.FE.ZS.xls
    my ($code, $name, $file) = split(/\;\;/, $str);
    $name=~s/^\"|\"$//g;
    $content.="<tr>";
    $linkxls = "/excel/$id/$file";
    $linkvisual = "/map/topic_$file"."_"."$id.html";
    $content.="<td>$name</td><td><a href=\"$linkxls\">XLS</a></td><td><a href=\"$linkvisual\" target=_blank>visualize</a></td>";
    $content.="</tr>\n";
}
$content.="</table>\n";

open(template, "/usr/local/apache2/alpha/cgi-bin/wiki/template.tpl");
@content = <template>;
close(template);
foreach $str (@content)
{
   $str=~s/\%\%content\%\%/$content/g;
   $str=~s/\%\%activevisualize\%\%/class\=\"active\"/gsix;
   push(@result, $str);
}

print "@result";
