var baseURL = '/api/v1';

var myApp = angular.module("myApp", ["ngRoute", "ngResource", "myApp.services"]);

var services = angular.module("myApp.services", ["ngResource"])
services
.factory('User', function($resource) {
    return $resource(baseURL + '/users/:id', {id: '@id'}, {
        get: { method: 'GET' }
    });
})
.factory('Users', function($resource) {
    return $resource(baseURL + '/users', {}, {
        query: { method: 'GET', isArray: true },
        create: { method: 'POST', }
    });
})
.factory('Search', function($resource) {
    return $resource(baseURL + '/search', {q: '@q'}, {
        query: { method: 'GET', isArray: true}
    });
});

myApp.config(function($routeProvider) {
    $routeProvider
    .when('/', {
        templateUrl: 'pages/main.html',
        controller: 'mainController'
    })
    .when('/users', {
        templateUrl: 'pages/users.html',
        controller: 'userListController'
    })
    .when('/users/:id', {
        templateUrl: 'pages/user_details.html',
        controller: 'userDetailsController'
    })
});

myApp.filter('filterStyles', function() {
  return function(input) {
    var output = new Array();
    for (i=0; i<input.length; i++) {
        if (input[i].checked == true) {
            output.push(input[i].name);
        }
    }
    return output;
  }
});

myApp.controller(
    'mainController',
    function ($scope, Search) {
        $scope.search = function() {
            q = $scope.searchString;
            if (q.length > 1) {
                $scope.results = Search.query({q: q});    
            }
        };
    }
);

myApp.controller(
    'userListController',
    function ($scope, Users, User, $location, $timeout) {
        if ($location.search().hasOwnProperty('created')) {
            $scope.created = $location.search()['created'];
        }
        if ($location.search().hasOwnProperty('deleted')) {
            $scope.deleted = $location.search()['deleted'];
        }
        $scope.users = User.query();
    }
);

myApp.controller(
    'userDetailsController', ['$scope', 'User', '$routeParams',
    function ($scope, User, $routeParams) {
        $scope.user = User.get({id: $routeParams.id});
    }
]);
