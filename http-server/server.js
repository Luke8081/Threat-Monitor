var express = require('express');
var fs = require('fs');
const path = require('path')
const router = express.Router()
const { exec } = require('node:child_process')

var app = express();

app.get('/', function(req, res) {
    res.sendFile(path.join(__dirname + '/templates/home.html'))
});

app.get('/addresses', function(req, res) {
    console.log("Load addresses")
});

app.get('/run', function(req, res) {
    console.log('Run button clicked')
    const to_run = "python3 " + process.cwd().replace("http-server", "vuln-Assesment.py")
    console.log(to_run)
    exec(to_run, (err, output) => {
        if (err){
            console.error('Could not run assesment.', err)
        }
        console.log(output)
    })
});

app.listen(8085, '127.0.0.1')

console.log("Waiting on port 8085")