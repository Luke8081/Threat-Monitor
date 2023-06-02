var express = require('express');
var fs = require('fs');
const path = require('path')
const router = express.Router()
const { exec } = require('node:child_process')

var app = express();

app.set('view engine', 'ejs')

function check_DIR(){
    //Change out of current working directory. This is so the program can find files needed
    var current_dir = process.cwd().split("/")
    if (current_dir[current_dir.length - 1] === "http-server"){
        process.chdir('../')
    }
}

function read_Log(){
    const data = fs.readFileSync("scan_log.txt", 'utf8');
    const array = data.split('.')
    var alert_count = 0
    for (var i = 0; i < array.length; i++){
        if (array[i] === " - ACTION NEEDED"){
            alert_count ++
        }
    }
    return alert_count
}

app.get('/', function(req, res) {
    check_DIR()
    alert_count = read_Log()

    var API_key = process.env.CRONITOR_API_KEY

    res.render("home", {alert_count: alert_count})
});

app.get('/addresses', function(req, res) {
    console.log("Load addresses")
});

app.get('/run', function(req, res) {
    console.log('Run button clicked')
    check_DIR()
    const to_run = "python3 " + process.cwd() + "/vuln-Assesment.py"
    console.log(to_run)
    exec(to_run, (err, output) => {
        if (err){
            console.error('Could not run assesment.', err)
        }
        console.log(output)
    })
    res.redirect('/')
});

app.listen(8085, '127.0.0.1')

console.log("Waiting on port 8085")