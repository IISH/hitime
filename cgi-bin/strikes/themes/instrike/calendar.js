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
                                        data: "%%jsondata%%",
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
                                        popitup("/strikes/timeline." + date.toISOString());
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
