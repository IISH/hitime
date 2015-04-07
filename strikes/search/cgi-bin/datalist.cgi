#!/usr/bin/perl

my $dir = "/usr/local/apache2/alpha/htdocs/clioinfra/datasets";

opendir(dir, $dir);
@datasets = readdir(dir);
closedir(dir);

print "Content-type: text/html\n\n";
#$content = "<table>\n";
#$content.= "<tr style=\"background-color:#A6C603\"><td><b>Indicator Name</b></td><td>Indicator Code</td><td>Excel</td><td>Visualize</td></tr>\n";
foreach $dataset (sort @datasets)
{
    if ($dataset!~/^\./)
    {
	my ($id, $datasetname) = ($dataset=~/^(\d+)\s*(.+)$/);
	$datasetname=~s/\s*\-\s*//g;
	$url = "/clioinfra/datasets/$dataset";
#	$content.="<h2> $datasetname </h2>\n";
        #$content.="<tr><td><h2> $datasetname </h2></td></tr>\n";

	opendir(dir, "$dir/$dataset");
	@data = readdir(dir);
	closedir(dir);

	my $nodata = 0;
	my $datacontent;
	my $row;
	foreach $file (@data)
	{
	    if ($file!~/^\./)
	    {
	  	$link = "/clioinfra/datasets/$dataset/$file";

		$true = 1;
		$true = 0 unless ($file=~/xls/i);

		if ($true)
		{
	           #$content.="<a href=\"$link\">$file</a><br>\n";
		   my $color = "#ffffff";
		   if ($row % 2 == 0)
		   {
			$color = "#efefef";
	  	   }
		   $row++;
		   $datacontent.="<tr align=center style=\"background-color:$color\" align=center>\n";
		   $code = ' - ';
		   if ($file) #=~/^.+\/(\S+)$/)
		   {
			$thisfile = $file;
		   }
		   $linkvisual = "http://alpha.dev.clio-infra.eu/map/file\_$dataset\-\-$thisfile.html";

		   $dataname = $file;
		   $file=~s/\.xls\S*//gsxi;
    		   $datacontent.="<td align=left>&nbsp;$file</td><td><a href=\"$link\">XLS</a></td><td><a href=\"$linkvisual\" target=_blank>visualize</a></td>";
    		   $datacontent.="</tr>\n";
		   $nodata++;
		};
	    };
	}	
	# A6C603
	$content.= "<table><tr style=\"background-color:#C9DB87\" align=left><td width=50%><b>$datasetname</b></td><td align=center>Excel</td><td align=center>Visualize</td></tr>\n" if ($datacontent);
	$content.="$datacontent" if ($datacontent);

	$content.="</table>\n" if ($datacontent);
    };
}
#$content.="</table>\n";

open(template, "/usr/local/apache2/alpha/cgi-bin/wiki/template.tpl");
@content = <template>;
close(template);
foreach $str (@content)
{
   $str=~s/\%\%content\%\%/$content/g;
   $str=~s/\%\%activedatasets\%\%/class\=\"active\"/gsix;
   push(@result, $str);
}

print "@result";

