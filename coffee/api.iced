window.api = {};
session_id = null;


request = (method, data, callback) ->
    if (session_id)
        data.session_id = session_id;
    url = 'http://logic.wartech.pro/' + method;
    $.ajax url, data, (reply) ->
      callback($.parseJSON(reply))

window.api.init = (callback) ->
    if (!$.cookie('session_id'))
        request 'init', {}, (reply) ->
            session_id = reply.session_id;
            $.cookie('session_id', session_id);
            callback();
    else
        session_id = $.cookie('session_id');
        callback();

window.api.getAllUsers = (callback) ->
    request('get_all_users', {}, callback);

window.api.requestFight = (fight_with, callback) ->
    request('request_fight', {fight_with: fight_with}, callback);

window.api.getAllModules = (callback) ->
    request('get_all_modules', {}, callback);

window.api.getUserRobot = (callback) ->
    request('get_user_robot', {}, callback);

window.api.getUserModules = (callback) ->
    request('get_user_modules', {}, callback);

window.api.setModuleToSlot = (slot_id, module_id, callback) ->
    request('set_module_to_slot', {
        slot_id: slot_id,
        module_id: module_id
    }, callback)

window.api.createNewUser = (callback) ->
    request('create_new_user', {}, callback);

window.api.login = (login, password, callback) ->
    request('login', {
        login: login,
        password: password
    }, callback);

