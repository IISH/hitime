﻿<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
	<head>
		<title>%%name%% - %%topic%%</title>
		<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />		
		<script type="text/javascript" src="swfobject.js"></script>
                <style type="text/css">
                <!--
                html { height:100%; }
                body {
                    height:100%;
                    margin: 0;
                    overflow-x: hidden;
                    overflow-y: hidden;
                }
                -->
                </style>

		<script type="text/javascript">
			
function getURLParam(strParamName){
  
				var strReturn = "";
  
				var strHref = window.location.href;
  
				if ( strHref.indexOf("?") > -1 ){
    
					var strQueryString = strHref.substr(strHref.indexOf("?"));
    
					var aQueryString = strQueryString.split("&");
    
					for ( var iParam = 0; iParam < aQueryString.length; iParam++ ){
      
						if ( aQueryString[iParam].indexOf(strParamName.toLowerCase() + "=") > -1 ){

							var aParam = aQueryString[iParam].split("=");
        
							strReturn = aParam[1];
        
							break;
      
						}
    
					}
					
				}
  
				return unescape(strReturn);

			}
			<!-- Adobe recommends that developers use SWFObject2 for Flash Player detection. -->
			<!-- For more information see the SWFObject page at Google code (http://code.google.com/p/swfobject/). -->
			<!-- Information is also available on the Adobe Developer Connection Under "Detecting Flash Player versions and embedding SWF files with SWFObject 2" -->
			<!-- Set to minimum required Flash Player version or 0 for no version detection -->
			var swfVersionStr = "9.0.45";
			<!-- xiSwfUrlStr can be used to define an express installer SWF. -->
			var xiSwfUrlStr = "";
			var flashvars = {};
			flashvars.location = getURLParam("l");
			flashvars.data = "%%dataset%%";
			var params = {};
			params.quality = "high";
			params.bgcolor = "#ffffff";
			params.play = "true";
			params.loop = "true";
			params.wmode = "window";
			params.allowfullScreen ="true";						
			params.scale = "showall";
			params.menu = "true";
			params.devicefont = "false";
			params.salign = "";
			params.allowscriptaccess = "sameDomain";
			var currentDate = new Date();
			var attributes = {};
			attributes.id = "StatPlanet";
			attributes.name = "StatPlanet";
			attributes.align = "middle";
			swfobject.createCSS("html", "height:100%; background-color: #ffffff; width:100%;");
			swfobject.createCSS("body", "margin:0; padding:0; overflow:hidden; height:100%; width:100%;");
			swfobject.embedSWF(
				"StatPlanet.swf?" + currentDate.getTime(), "flashContent",
				"100%", "100%",
				swfVersionStr, xiSwfUrlStr,
				flashvars, params, attributes);		
		</script>		
	</head>
	<body>
		<!-- SWFObject's dynamic embed method replaces this alternative HTML content for Flash content when enough JavaScript and Flash plug-in support is available. -->
		<div id="flashContent">
			<a href="http://www.adobe.com/go/getflash">
				<img src="http://www.adobe.com/images/shared/download_buttons/get_flash_player.gif" alt="Get Adobe Flash player" />
			</a>
			<p>This page requires Flash Player version 9.0.45 or higher.</p>
		</div>
	</body>
</html>
