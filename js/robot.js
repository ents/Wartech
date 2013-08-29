robot = {
    init: function(callback){
        var robot;
        var modules;
        var userModules;

        api.getUserRobot(function(_robot){
            template.load('hull/' + _robot.hull_name, function(reply){
                robot = _robot;
                $('.hull').html(reply).addClass(robot.hull_name);
                processIfLoaded();
            });
        });
        api.getAllModules(function(_modules){
            modules = _modules;
            processIfLoaded();
        });
        api.getUserModules(function(_modules){
            userModules = _modules;
            processIfLoaded();
        });

        function processIfLoaded(){
            if (robot && modules && userModules) {
                callback();
            }
        }
    }
}