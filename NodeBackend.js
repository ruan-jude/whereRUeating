const express = require('express');
const request = require('request');

const app = express()

const HOSTNAME = '172.16.122.27';
const PORT = '8080';

// ===== FLASK => NODE CONNECTION =====
// ===== CONNECTS HTML FILES TO URL =====
app.get('/', (req, res) => {
    request('http://'+HOSTNAME+':'+PORT+'/Home/', function (err, resp, body) {
        console.error('error:', err);
        console.log('statusCode:', resp && response.statusCode);
        console.log('body:', body);
        res.send(body);
    });
});

app.get('/Login/', (req, res) => {
    request('http://'+HOSTNAME+':'+PORT+'/Login/', function (err, resp, body) {
        console.error('error:', err);
        console.log('statusCode:', resp && response.statusCode);
        console.log('body:', body);
        res.send(body);
    });
});

app.get('/CreateAccount/', (req, res) => {
    request('http://'+HOSTNAME+':'+PORT+'/CreateAccount/', function (err, resp, body) {
        console.error('error:', err);
        console.log('statusCode:', resp && response.statusCode);
        console.log('body:', body);
        res.send(body);
    });
});

app.get('/Search/', (req, res) => {
    request('http://'+HOSTNAME+':'+PORT+'/Search/', function (err, resp, body) {
        console.error('error:', err);
        console.log('statusCode:', resp && response.statusCode);
        console.log('body:', body);
        res.send(body);
    });
});

app.get('/UserSettings/', (req, res) => {
    request('http://'+HOSTNAME+':'+PORT+'/UserSettings/', function (err, resp, body) {
        console.error('error:', err);
        console.log('statusCode:', resp && response.statusCode);
        console.log('body:', body);
        res.send(body);
    });
});

app.get('/UserHome/', (req, res) => {
    request('http://'+HOSTNAME+':'+PORT+'/UserHome/', function (err, resp, body) {
        console.error('error:', err);
        console.log('statusCode:', resp && response.statusCode);
        console.log('body:', body);
        res.send(body);
    });
});

app.listen(PORT, function (){ 
    console.log('Listening on Port 8080');
});


