template = {
    load: function(url, callback){
        $.get('template/' + url + '.html', {}, function(reply){
            callback(reply);
        });
    }
}