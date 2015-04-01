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

    var dataStream = $websocket('ws://' + location.hostname + ':8766/firehose');
    dataStream.socket.binaryType = 'arraybuffer';

    if (! dataStream === 0) {
      throw 'got no data';
    }

    dataStream.onMessage(function(message) {
      for (var i=0; i<(message.data.byteLength/3); i++) {
        data.data[i] = new Uint8Array(message.data, i*3, 3);
      }
      data.timestamp = (new Date());
    });

    return data;
  })

  .directive('neopixel', function() {
      // constants
      var margin = 20,
        width = 600,
        height = 600,
        radius = ~~(width/105.0), // convert to int
        color = d3.interpolateRgb("#f77", "#77f"),
        // N=420
        x1 = 105,
        y1 = 105,
        x2 = 105,
        y2 = 105;

      return {
        restrict: 'E',
        scope: {
          data: '=',
        },
        link: function (scope, element, attrs) {
          console.log(element);
          var iToXY = function(i) {
            var ret = null;
            if (i < y1) {
              ret = [~~(x1*radius), ~~(i*radius)];
            } else if (i >= y1 && i < (x2+y1)) {
              ret = [~~((y1+x2-i)*radius), ~~(y1*radius)];
            } else if (i >= (y1+x2) && i < (y1+x2+y2)) {
              ret = [0, ~~((y1+x1+y2-i)*radius)];
            } else {
              ret = [~~((i-(y1+y2+x2))*radius), 0];
            }
            return ret;
          };

          var container = d3.select(element[0]);
          var svg = container.append("svg")
              .attr("width", width)
              .attr("height", height);

          scope.$watch('data.timestamp', function() {
            var shp = svg.selectAll("rect").data(scope.data.data); // identity function to update existing
            shp
            .style('fill', function(d) {return d3.rgb(d[0],d[1],d[2])})
            .enter()
            .append("rect")
            .attr('x', function(d,i){ return iToXY(i)[0];})
            .attr('y', function(d,i){ return iToXY(i)[1];})
            .attr('width', radius)
            .attr('height', radius);
            shp.exit().remove();
          },true);
        }
      }

    });

