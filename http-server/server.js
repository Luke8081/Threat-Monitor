var express = require('express');
var fs = require('fs');

var app = express.createServer();

var app = express();
app.get('/', function(req, res) {
    res.render('home.html', {root: __dirname })
});

app.listen(8081, '127.0.0.1')