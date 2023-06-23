var express = require('express');
var fs = require('fs');
const path = require('path')
const router = express.Router()
const { exec } = require('node:child_process')
const sqlite = require('sqlite3').verbose()
var partials = require('express-partials')

var app = express();

app.set('view engine', 'ejs')
//app.use(partials())
app.use(express.static(__dirname + '/views'));

function check_DIR(){
    //Change out of current working directory. This is so the program can find files needed
    var current_dir = process.cwd().split("/")
    if (current_dir[current_dir.length - 1] === "http-server"){
        process.chdir('../')
    }
}

//Async function where you can parse a SQL query
async function db_all(query){
    check_DIR()
    //Connect to database
    let db = new sqlite.Database(process.cwd() + '/reports/database.db', sqlite.OPEN_READONLY, (err) => {
        if (err){
            console.error(err.message)
        }
    })
    return new Promise(function(resolve,reject){
        db.all(query, function(err,rows){
           if(err){return reject(err);}
           resolve(rows);
         });
        db.close()
    });
}

//Gets the sum of alerts for all the websites scanned
async function get_alerts(){
    let database = await db_all('SELECT SUM(Low_Alert) AS Low_Alert, SUM(Medium_Alert) AS Medium_Alert, SUM(High_Alert) AS High_Alert FROM alert_summary')
    return{
        Low_Alert: database[0].Low_Alert,
        Medium_Alert: database[0].Medium_Alert,
        High_Alert: database[0].High_Alert
    }
}

async function get_scanned_addresses(){
    let sql = "SELECT Address FROM alert_Summary"
    let addresses = await db_all(sql)
    addresses = addresses[0].Address
    return addresses
}

app.get('/', async function(req, res) {
    check_DIR()

    var API_key = process.env.CRONITOR_API_KEY
    const alerts = await get_alerts()
    console.log(alerts)

    res.render("home", {alerts: alerts})
});

app.get('/addresses', async function(req, res) {
    console.log("Load addresses")
    res.render('addresses')
    let addresses = await get_scanned_addresses()
    console.log(addresses)
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