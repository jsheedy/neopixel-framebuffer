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
      firehoseSocket.send(0);

    }
    reader.readAsArrayBuffer(event.data);
  };
  // Listen for socket closes
  socket.onclose = function(event) {
    console.log('Client notified socket has closed',event);
  };
};