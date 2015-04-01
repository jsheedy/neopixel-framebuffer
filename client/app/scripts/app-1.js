'use strict';

/**
 * @ngdoc overview
 * @name angularApp
 * @description
 * # angularApp
 *
 * Main module of the application.
 */
angular
  .module('angularApp', [
    'ngResource',
    'ngRoute',
    'ngWebSocket'
  ])
  .config(function ($routeProvider) {
    $routeProvider
      .when('/', {
        templateUrl: 'views/main.html',
        controller: 'MainCtrl'
      });
  })

  .factory('firehose', function($websocket) {
    // Open a WebSocket connection

    var data = {data: []};

    var dataStream = $websocket('ws://localhost:8766/firehose');
    if (! dataStream === 0) {
      throw 'got no data';
    }

    dataStream.onMessage(function(message) {
      var x = JSON.parse(message.data);
      var tuples = x.length / 3;
      var arr = [];
      for (var i=0; i<tuples; i++) {
        arr.push(x.slice(i*3, i*3+3));
      }
      data.data = arr;
    });

    return data;
  })
  .directive('neopixel', function() {
      // constants
      var margin = 20,
        width = 800,
        height = 800,
        radius = width/16,
        color = d3.interpolateRgb("#f77", "#77f");

      return {
        restrict: 'E',
        scope: {
          data: '=',
        },
        link: function (scope, element, attrs) {

          console.log('foo',element);
          var scale = d3.scale.linear().domain([0,16]).range([0,width])
          // set up initial svg object
          var vis = d3.select(element[0])
            .append("svg")
              .attr("width", width)
              .attr("height", height);

              scope.$watch('data', function() {
                vis.selectAll("*").remove();
                var shp = vis.selectAll("rect").data(scope.data.data);
                shp
                .enter()
                .append("rect")
                // .attr("cx",function(d,i) {return radius+scale(i%16);})
                // .attr("cy",function(d,i) { return radius+scale(Math.floor(i/16));})
                // .attr("r",function(d) { return radius})
                .attr('x', function(d,i) {return radius+scale(i%16);})
                .attr('y',function(d,i) { return radius+scale(Math.floor(i/16));})
                .attr('width', radius)
                .attr('height', radius)
                .style('fill', function(d) {return d3.rgb(d[0],d[1],d[2])});
                shp.exit().remove();
              },true);
        }
      }

    });

