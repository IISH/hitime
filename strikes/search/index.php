<?
/**
* QueryBox 1.0
* @author marcos weskamp
* @published: Nov 20, 2008.
* Copyright 2008, Marcos Weskamp marcos@marumushi.com
* This work is licensed under a Creative Commons Attribution 3.0 Unported License. 
* http://creativecommons.org/licenses/by/3.0/
**/

$web_root 	=  dirname($_SERVER['PHP_SELF']).'/';

$query 	     = !empty($_GET['q']) ? $_GET['q'] : null;

?>
<html>

<head>
	<title>Evergreen Library Quick Search</title>
	<link rel="stylesheet" media="screen" href="<?=$web_root?>../css/querybox.css" type="text/css" />
	<script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/dojo/1.2.0/dojo/dojo.xd.js"></script>
	<script type="text/javascript" src="<?=$web_root?>../js/marumushi.widget.querybox.js"></script>
</head>

<body>
	
	<script type="text/javascript">

		var qbox 				= new marumushi.widget.QueryBox('/cgi-bin/offline/search_lib.cgi?q=','qbox');
		qbox.defaultMessage 	= "Search something in library...";
		qbox.getItemMarkup 		= function(item){
			//I'm feeling lucky!
			var url = "http://www.google.com/search?hl=en&btnI=I%27m+Feeling+Lucky&aq=f&q=";
			return '<div class="ListItem"><a href="'+item.link+'"><h2>'+item.title+'</h2>'+item.description+'</a></div>';
		}
	</script>

	<div id="qbox"><!-- querybox will get rendered here --></div>
	
</body>
</html>


