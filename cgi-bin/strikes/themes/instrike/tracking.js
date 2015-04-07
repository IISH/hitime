<script type="text/javascript">

var m = [20, 10, 20, 10],
    w = 180 - m[1] - m[3],
    h = 59 - m[0] - m[2],
    parse = d3.time.format("%b %Y").parse;

// Scales. Note the inverted domain for the y-scale: bigger is up!
var x = d3.time.scale().range([0, w]),
    y = d3.scale.linear().range([h, 0]);

// An area generator, for the light fill.
var area = d3.svg.area()
    .interpolate("monotone")
    .x(function(d) { return x(d.date); })
    .y0(h)
    .y1(function(d) { return y(d.price); });

// A line generator, for the dark stroke.
var line = d3.svg.line()
    .interpolate("monotone")
    .x(function(d) { return x(d.date); })
    .y(function(d) { return y(d.price); });

d3.csv("%%csvdatafile%%", function(data) {

  // Nest values by symbol.
  var symbols = d3.nest()
      .key(function(d) { return d.symbol; })
      .entries(data);

  // Parse dates and numbers. We assume values are sorted by date.
  // Also compute the maximum price per symbol, needed for the y-domain.
  symbols.forEach(function(s) {
    s.values.forEach(function(d) { d.date = parse(d.date); d.price = +d.price; });
    s.maxPrice = d3.max(s.values, function(d) { return d.price; });
  });

  // Compute the minimum and maximum date across symbols.
  x.domain([
    d3.min(symbols, function(s) { return s.values[0].date; }),
    d3.max(symbols, function(s) { return s.values[s.values.length - 1].date; })
  ]);

  // Add an SVG element for each symbol, with the desired dimensions and margin.
  var svg = d3.select("#visual").selectAll("svg")
      .data(symbols)
    .enter().append("svg:svg")
      .attr("width", w + m[1] + m[3])
      .attr("height", h + m[0] + m[2])
    .append("svg:g")
      .attr("transform", "translate(" + m[3] + "," + m[0] + ")");

  // Add the area path elements. Note: the y-domain is set per element.
  svg.append("svg:path")
      .attr("class", "area")
      .attr("d", function(d) { y.domain([0, d.maxPrice]); return area(d.values); });

  // Add the line path elements. Note: the y-domain is set per element.
  svg.append("svg:path")
      .attr("class", "line")
      .attr("d", function(d) { y.domain([0, d.maxPrice]); return line(d.values); });

  // Add a small label for the symbol name.
  svg.append("svg:text")
      .attr("class", "text")
      .attr("x", w - 6)
      .attr("y", h + 10 )
      .attr("text-anchor", "end")
      .style("font-size","9px")
      .text(function(d) { return d.key; });
});

</script>
