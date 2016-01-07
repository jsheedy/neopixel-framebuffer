var Neopixel = function(container) {

  // var div = d3.select('.neopixel');

  // function getElementDimensions() {
  //    return { 'h': div.offsetHeight, 'w': div.offsetWidth };
  //  };

  // constants
  var width = 500,
    height = 500,
    radius = width/105.0,
    color = d3.interpolateRgb("#f77", "#77f"),
    // N=420
    x1 = 105,
    y1 = 105,
    x2 = 105,
    y2 = 105;

  var iToXY = function(i) {
    var ret = null;
    if (i < y1) {
      ret = [width-radius, i*radius];
    } else if (i >= y1 && i < (x2+y1)) {
      ret = [width - (i-y1)*radius, width-radius];
    } else if (i >= (y1+x2) && i < (y1+x2+y2)) {
      ret = [0, ~~((y1+x1+y2-i)*radius)];
    } else {
      ret = [~~((i-(y1+y2+x2))*radius), 0];
    }
    return ret;
  };

  var svg = container.append("svg")
      .attr("width", width)
      .attr("height", height)
      .style('position', 'absolute');

  this.draw = function(data) {
    // var arr = new Uint8Array(e.target.result);
    var parsedData = [];
    for (var i=0; i<(data.byteLength/3); i++) {
      parsedData[i] = new Uint8Array(data, i*3, 3);
    }
    var shp = svg.selectAll("rect").data(parsedData); // identity function to update existing
    shp
      .style('fill', function(d) {return d3.rgb(d[0],d[1],d[2])})
      .enter()
      .append("rect")
      .attr('x', function(d,i){ return iToXY(i)[0];})
      .attr('y', function(d,i){ return iToXY(i)[1];})
      .attr('width', radius)
      .attr('height', radius);
    shp.exit().remove();
  }

};

module.exports = Neopixel;

