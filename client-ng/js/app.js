(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
// var Data = require('./data.js');
// var osc = require("osc.js");
var Neopixel = require("./neopixel.js");

var container = d3.select('.neopixel');

var neopixel = new Neopixel(container);
var con = document.getElementById('console');
var body = d3.select('body');
var conColumns = {};

function handleOSC(message) {
  logOSC(message);
  if (message.address === '/metronome') {
    strobe(message);
  }
}

function strobe(message) {
  var bpm = message.args[0];
  var delay = 0; // (60 / bpm) / 4.0;
  var duration = (60.0 / bpm) * 1000 / 2.0;
  body
    .style('background-color', '#000')
    .transition()
    .delay(delay)
    .duration(duration)
    .style('background-color','white');
}

function logOSC(message) {
  var div = document.createElement('div');
  div.textContent = message.address + ' ' + message.args;
  var colId = message.address.replace(/\//g,'');
  var col = conColumns[colId];
  if (! col) {
    col = document.createElement('div');
    conColumns[colId] = col;
    con.appendChild(col);
  }
  col.appendChild(div);
  if (col.childNodes.length > 34) {
    col.removeChild(col.firstChild);
  }
  col.scrollTop = col.scrollHeight;
}

var hostName = window.location.hostname;

var socket = new WebSocket('ws://' + hostName + ':8766/osc');
socket.onopen = function(event) {

  socket.onmessage = function(event) {
    reader = new FileReader();
    reader.onloadend = function(e) {
      var arr = new Uint8Array(e.target.result);
      var message = osc.readMessage(arr);
      handleOSC(message);
    }
    reader.readAsArrayBuffer(event.data);
  };

  // Listen for socket closes
  socket.onclose = function(event) {
    console.log('Client notified socket has closed',event);
  };
};


var firehoseSocket = new WebSocket('ws://' + hostName + ':8766/firehose');
firehoseSocket.onopen = function(event) {
  firehoseSocket.onmessage = function(event) {
    reader = new FileReader();
    reader.onloadend = function(e) {
      neopixel.draw(e.target.result);
      // firehoseSocket.send(0);

    }
    reader.readAsArrayBuffer(event.data);
  };
  // Listen for socket closes
  socket.onclose = function(event) {
    console.log('Client notified socket has closed',event);
  };
};
},{"./neopixel.js":2}],2:[function(require,module,exports){
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


},{}]},{},[1]);
