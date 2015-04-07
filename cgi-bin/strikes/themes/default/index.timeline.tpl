<html>
        <head>
	<title>Strikes</title>
    	<meta name="description" content="100 years of books publishing" />
        <link href="http://netdna.bootstrapcdn.com/twitter-bootstrap/2.3.1/css/bootstrap-combined.min.css" rel="stylesheet">
        <link href="http://netdna.bootstrapcdn.com/font-awesome/3.0.2/css/font-awesome.css" rel="stylesheet">
        <link rel="stylesheet" href="/strikes/calendar/cal-heatmap.css?v=2.1.0" />
        <link rel="stylesheet" href="/strikes/calendar/main.css?v=2.1.0" />
        <link href='http://fonts.googleapis.com/css?family=Droid+Sans:400:700' rel='stylesheet' type='text/css'>
        <script type="text/javascript" src="http://d3js.org/d3.v3.min.js"></script>
        <script type="text/javascript" src="/strikes/calendar/cal-heatmap.min.js?v=2.1.6"></script>
        <script type="text/javascript" src="/strikes/calendar/moment.min.js"></script>
        <script type="text/javascript" src="/strikes/calendar/lang.min.js"></script>
        <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
        <script type="text/javascript" src="http://netdna.bootstrapcdn.com/twitter-bootstrap/2.3.1/js/bootstrap.min.js"></script>

                <script type="text/javascript" src="/kb/charts/swfobject.js"></script>
                <script type="text/javascript">

                        swfobject.embedSWF(
                        "/kb/charts/open-flash-chart.swf", "my_chart223",
                        "100%", "400", "9.0.0", "/kb/charts/expressInstall.swf",
                        {"data-file":"%%datafile%%"} );

                </script>
        </head>

        <body>
	<table border=0 width=100%>
	<tr>
	<td width=20%" valign=top>

        <div class="ftr">
                        <h1></h1>
                        <div class="bs-docs-example">


                        <div id="cal-heatmap">

                        </div>

                        <script language="javascript" type="text/javascript">
                        <!--
                        function popitup(url) {
                                newwindow=window.open(url,'name');
                                if (window.focus) {newwindow.focus()}
                                return false;
                        }

                        // -->
                        </script>

                        <script type="text/javascript">
                                moment.lang('fr');
                                var calendar = new CalHeatMap();
                                calendar.init({
                                        data: "/strikes/data/%%thisyear%%.txt",
                                        domain: "month",
                                        subDomain: "x_day",
                                        start : new Date(%%thisyear%%, 00),
                                        range: 12,
                                        browsing: true,
                                        browsingOptions: {
                                                previousLabel : "<i class=\"icon-chevron-left\"></i>",
                                                nextLabel: "<i class=\"icon-chevron-right\"></i>"
                                        },
                                        cellSize: 10,
                                        cellPadding: 1,
                                        verticalOrientation: "true",
                                        onClick: function(date, count) {
                                        $("#onClick-placeholder").html(count + " strikes occured on " + date.toISOString());
                                        popitup("/strikes/timeline." + "%%thisyear%%-01");
                               },
                                        scale: [10, 30, 100, 200],
                                        legend: [1, 2, 3, 4],
                                        label:
                                        {
                                                position: "left",
                                                width: 100
                                        }
                                });
                        </script>
                        </div>

                                                <div>
                                        <span id="onClick-placeholder">Click a date on the calendar</span>
                                </div>
        </div>
	</td>
	<td width=70% valign=top>
                <center>
                <h2>%%title%%</h2>
                <p>%%period%%</p>
                <p>%%refine%%</p>
                </center>

		<div>
		<a href="/cgi-bin/strikes/index.cgi">Charts</a>&nbsp;<a href="#">Timelines</a>&nbsp;<a href="/charts/maps/StatPlanet_Netherlands/strikes.html">Maps</a>
		</div>
                <object style="visibility: visible;" id="my_chart223" data="/kb/charts/open-flash-chart.swf" type="application/x-shockwave-flash" height="300" width="550"></object>

		%%events%%
	</td>
	<td width=10%>&nbsp;</td>
	</table>
        </body>
 </html>

