<!DOCTYPE html>
<meta charset="utf-8">
<head>
<style>

body {
}

.axis path,
.axis line {
  fill: none;
  stroke: #000;
  shape-rendering: crispEdges;
}

.x.axis path {
  display: none;
}

.line {
  fill: none;
  stroke: steelblue;
  stroke-width: 1.5px;
}

</style>
</head>
<body>
<center>
		%%refine%%
</center>
		<br />
                <center>
                <h2>%%title%%</h2>
                <p>%%menu%%</p>
                <p>%%period%%</p>
                </center>

                <div style="float:left; width:400px;vertical-align:top;">
                        %%navigation_level1%%
                </div>
                <div style="float:right; width:400px;vertical-align:top;">
                        %%navigation_level2%%
                </div>

<script src="http://d3js.org/d3.v3.js"></script>
<div style="float:right;width:30%">
<script>

var margin = {top: 10, right: 10, bottom: 30, left: 350},
    width = 1200 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;

var parseDate = d3.time.format("%Y-%m-%d").parse;

var x = d3.time.scale()
    .range([0, width]);

var y = d3.scale.linear()
    .range([height, 0]);

var xAxis = d3.svg.axis()
    .scale(x)
    .orient("bottom");

var yAxis = d3.svg.axis()
    .scale(y)
    .orient("left");

var line = d3.svg.line()
    .x(function(d) { return x(d.date); })
    .y(function(d) { return y(d.close); });

var svg = d3.select("body").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

d3.tsv("%%tsvdatafile%%", function(error, data) {
  data.forEach(function(d) {
    d.date = parseDate(d.date);
    d.close = +d.close;
  });

  x.domain(d3.extent(data, function(d) { return d.date; }));
  y.domain(d3.extent(data, function(d) { return d.close; }));

  svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis);

  svg.append("g")
      .attr("class", "y axis")
      .call(yAxis)
    .append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 6)
      .attr("dy", ".71em")
      .style("text-anchor", "end")
      .text("");

  svg.append("path")
      .datum(data)
      .attr("class", "line")
      .attr("d", line);
});

</script>
</div>
		<div>
                <center>%%chartdescription%%</center>
                </div>
                %%events%%
</body>
