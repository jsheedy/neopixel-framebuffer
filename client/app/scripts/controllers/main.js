'use strict';

angular.module('angularApp')
  .controller('MainCtrl', function ($scope, $rootScope, firehose) {
    // $scope.MyData = MyData;
    // $scope.MyData.get();

    var data = [];
    for (var i=0; i<256; i++) {
        data.push([i,255-i,0]);
    }
    // $rootScope.data = {data: data};

    var noData = function() {
      console.debug('using test data, we do not have a websockets source');
      setInterval(function() {
        var n = 256;
        for(var i=0; i<n; i++) {
          data[i] = [parseInt(Math.random()*256), parseInt(Math.random()*256), parseInt(Math.random()*256)];
        }
        $rootScope.data.data = data;
      }, 200);
    };

    $scope.data = firehose;
  });
