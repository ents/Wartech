window.robot = {};


window.robot.init = (callback) ->
    await
      api.getUserRobot defer _robot
      api.getAllModules deffer allModules
      api.getUserModules deffer userModules
    
    cb
    modules = allModules;
    userModules = _modules;
    robot = _robot;
    url = 'hull/' + _robot.hull_name;
    await template.load url, (reply) ->
    cb $('.hull').html(reply).addClass(robot.hull_name);
    callback();
