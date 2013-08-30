window.template = {};

window.template.load = (url, callback) ->
	url = 'template/' + url + '.html';
	$.get url, (reply) ->
		callback(reply);

