<?php
//header('content-type: text/javascript');
$action = $_GET['action'];
$get = $_GET;
unset($get['action']);
if ($action == 'init') {
	die(json_encode(array('session_id' => md5(uniqid()))));
}
$url = "http://wartech.algo.pw/$action?".http_build_query($get);
echo file_get_contents($url);
