(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
// var Data = require('./data.js');
// var osc = require("osc.js");

// var socket = new WebSocket('ws://localhost:8766/osc');
// // Open the socket
// socket.onopen = function(event) {

//     // Send an initial message
//     // socket.send('I am the client and I\'m listening!');

//     // Listen for messages
//     socket.onmessage = function(event) {
//         console.log('Client received a message: ',event);
//     };

//     // Listen for socket closes
//     socket.onclose = function(event) {
//         console.log('Client notified socket has closed',event);
//     };

//     //socket.close()

// };

var oscPort = new osc.WebSocketPort({
    url: "ws://localhost:8766/osc" // URL to your Web Socket server.
});
oscPort.on("message", function (oscMsg) {
    console.log("An OSC message just arrived!", oscMsg);
});

},{}]},{},[1]);
