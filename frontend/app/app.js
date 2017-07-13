var baseURL = '/api/v1';
var myApp = angular.module("myApp", ["ngRoute", "ngResource", "myApp.services"]);
var services = angular.module("myApp.services", ["ngResource"])

services
    .factory('User', function($resource) {
        return $resource(baseURL + '/users/:id', { id: '@id' }, {
            get: { method: 'GET' }
        });
    })
    .factory('Search', function($resource) {
        return $resource(baseURL + '/search', { q: '@q' }, {
            query: { method: 'GET', isArray: true }
        });
    });

myApp.config(function($routeProvider) {
    $routeProvider
        .when('/', {
            templateUrl: 'pages/main.html',
            controller: 'mainController'
        })
        .when('/users/:id', {
            templateUrl: 'pages/user_details.html',
            controller: 'userDetailsController'
        })
});

myApp.directive('focus',
    function($timeout) {
        return {
            scope: {
                trigger: '@focus'
            },
            link: function(scope, element) {
                scope.$watch('trigger', function(value) {
                    if (value === "true") {
                        $timeout(function() {
                            element[0].focus();
                        });
                    }
                });
            }
        };
    });

myApp.controller('mainController', ['$scope', 'Search',
    function($scope, Search) {
        $scope.search = function() {
            q = $scope.searchString;
            if (q.length > 1) {
                $scope.results = Search.query({ q: q });
            }
        };
    }
]);

myApp.controller('userDetailsController', ['$scope', 'User', '$routeParams',
    function($scope, User, $routeParams) {
	var now = Math.floor(Date.now() / 1000);
        $scope.reports = [];
        $scope.user = User.get({ id: $routeParams.id },
            function(user) {
                // Some query strings that we can replace for the bottom
                // search links we provide on the details page.
                var name = user.fullname.replace(' ', '+');
                var email = /@([^\.]+)/.exec(user.email)[1];
                var company = user.company
                                .replace(', INC', '')
                                .replace('.', '')
                                .replace(' ', '+');
                $scope.linkedinsearchstring = name + '+' + company + '+' + email;
                $scope.namesearchstring = name;
                var then = user.hiredate;
		var years = (now - then) / (356.0 * 24.0 * 60.0 * 60.0);
		if( then == 0 ) {
			years = 0;
		}
		$scope.time_at_company = years;

                // We can now also go through the list of reports and populate that list
                for (var i = 0; i < user.reports.length; i++) {
                    var myid = user.reports[i];
                    if (myid.length > 0) {
                        $scope.reports.push(User.get({ id: myid }));
                    }
                }
            }
        );
    }
]);


myApp.controller('footerController', ['$scope', '$http',
    function($scope, $http) {
        $http.get(baseURL + '/health').then( function(response) {
            $scope.health = response.data;
            console.log($scope.health);
        });
    }
]);
