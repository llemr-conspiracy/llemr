
drawpie = function(data, div_name){
  // sum of all values in dictionary data
  const sumValues = obj => Object.values(obj).reduce((a, b) => a + b);

  var data_sum = sumValues(data)

  // set the dimensions and margins of the graph
  var width = d3.select(div_name).node().getBoundingClientRect().width
      height = window.innerHeight * 0.8
      margin = window.innerHeight * 0.075

  // The radius of the pieplot is half the width or half the height (smallest one). I subtract a bit of margin.
  var radius = Math.min(width, height) / 2 - margin

  // append the svg object to the div called div_name
  var svg = d3.select(div_name)
    .append("svg")
      .attr("width", width)
      .attr("height", height)
    .append("g")
      .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");

  // Create dummy data
  //var data = {a: 9, b: 20, c:30, d:8, e:12}

  // set the color scale
  var color = d3.scaleOrdinal()
    .domain(data)
    .range(d3.schemeTableau10);

  // Compute the position of each group on the pie:
  var pie = d3.pie()
    .value(function(d) {return d.value; })
  var data_ready = pie(d3.entries(data))
  // Now I know that group A goes from 0 degrees to x degrees and so on.

  // shape helper to build arcs:
  var arcGenerator = d3.arc()
    .innerRadius(0)
    .outerRadius(radius)

  // Build the pie chart: Basically, each part of the pie is a path that we build using the arc function.
  svg
    .selectAll('mySlices')
    .data(data_ready)
    .enter()
    .append('path')
      .attr('d', arcGenerator)
      .attr('fill', function(d){ return(color(d.data.key)) })
      .attr("stroke", "black")
      .style("stroke-width", "2px")
      .style("opacity", 0.7)

  // Now add the annotation. Use the centroid method to get the best coordinates
  svg
    .selectAll('mySlices')
    .data(data_ready)
    .enter()
    .append('text')
    .text(function(d){
      if(d.data.value>0)
        return d.data.key+': '+(d.data.value*100/data_sum).toFixed(1) + '%'
      else
        return ''})
    .attr("transform", function(d) { return "translate(" + arcGenerator.centroid(d) + ")";  })
    .style("text-anchor", "middle")
    .style("font-size", 16)
    .style("font-weight", 700)
}
