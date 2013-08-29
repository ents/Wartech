api = (function()
{
    var session_id = null;
    function request(method, data, callback){
        if (session_id)
            data.session_id = session_id;
        $.ajax({
            url: 'http://wartech.algo.pw/' + method,
            data: data
        }).done(function(reply){
            callback($.parseJSON(reply));
        });
    }

    return {
        init: function(callback){
            if (!$.cookie('session_id')){
                request('init', {}, function(reply){
                    session_id = reply.session_id;
                    $.cookie('session_id', session_id);
                    callback();
                });
            } else {
                session_id = $.cookie('session_id');
                callback();
            }
        },
        getAllUsers: function(callback){
            request('get_all_users', {}, callback);
        },
        requestFight: function(fight_with, callback) {
            request('request_fight', {
                fight_with: fight_with
            }, callback);
        },
        getAllModules: function(callback){
            request('get_all_modules', {}, callback);
        },
        getUserRobot: function(callback){
            request('get_user_robot', {}, callback);
        },
        getUserModules: function(callback){
            request('get_user_modules', {}, callback);
        },
        setModuleToSlot: function(slot_id, module_id, callback) {
            request('set_module_to_slot', {
                slot_id: slot_id,
                module_id: module_id
            }, callback)
        },
        createNewUser: function(){
            request('create_new_user', {}, callback);
        },
        login: function(login, password, callback){
            request('login', {
                login: login,
                password: password
            }, callback);
        }
    };
})();
