const express = require('express');
const http = require('http');
const url = require('url');
const fs = require('fs');

const app = express()

const HOSTNAME = '172.16.122.27';
const PORT = 8080;

app.get('', (req, res) => {
	res.sendFile(__dirname + '/client/HomePage.html');
});

app.get('/LoginPage.html', (req, res) => {
	res.sendFile(__dirname + '/client/LoginPage.html');
});

const SERVER = http.createServer((req, res) => {
  res.statusCode = 200;
  res.setHeader('Content-Type', 'text/plain');
  res.end('Hello, World!\n');
});

app.listen(PORT, HOSTNAME, () => {
  console.log(`Server running at http://${HOSTNAME}:${PORT}/`);
});
