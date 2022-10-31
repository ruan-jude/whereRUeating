const express = require('express');
const request = require('request');
const http = require('http');
const url = require('url');
const fs = require('fs');

const app = express()

const HOSTNAME = '172.16.122.27';
const PORT = 3030;

// ===== FLASK => NODE CONNECTION =====
// ===== CONNECTS HTML FILES TO URL =====
app.get('', (req, res) => {
	request('http://'+HOSTNAME+':'+PORT, function (err, resp, body) {
		console.error('error:', err);
		console.log('statusCode:', resp && response.statusCode);
		console.log('body:', body);
		res.send(body);
	});
});

app.get('/Login.html', (req, res) => {
	request('http://'+HOSTNAME+':'+PORT+'/Login.html', function (err, resp, body) {
		console.error('error:', err);
		console.log('statusCode:', resp && response.statusCode);
		console.log('body:', body);
		res.send(body);
	});
});

app.get('/CreateAccount.html', (req, res) => {
	request('http://'+HOSTNAME+':'+PORT+'/CreateAccount.html', function (err, resp, body) {
		console.error('error:', err);
		console.log('statusCode:', resp && response.statusCode);
		console.log('body:', body);
		res.send(body);
	});
});

app.get('/Search.html', (req, res) => {
	request('http://'+HOSTNAME+':'+PORT+'/Search.html', function (err, resp, body) {
		console.error('error:', err);
		console.log('statusCode:', resp && response.statusCode);
		console.log('body:', body);
		res.send(body);
	});
});

app.get('/UserSettings.html', (req, res) => {
	request('http://'+HOSTNAME+':'+PORT+'/UserSettings.html', function (err, resp, body) {
		console.error('error:', err);
		console.log('statusCode:', resp && response.statusCode);
		console.log('body:', body);
		res.send(body);
	});
});

// ===== STARTS THE SERVER =====
app.listen(PORT, HOSTNAME, () => {
  console.log(`Server running at http://${HOSTNAME}:${PORT}/`);
});
