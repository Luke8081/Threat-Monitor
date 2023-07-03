var express = require('express');
var fs = require('fs');
const path = require('path')
const router = express.Router()
const { exec } = require('node:child_process')
const sqlite = require('sqlite3').verbose()

var app = express();

app.set('view engine', 'ejs')
//app.use(partials())
app.use(express.static(__dirname + '/views'));
app.use(express.json())

var status = "Not running"
var console_text = ""

function check_DIR(){
    //Change out of current working directory. This is so the program can find files needed
    var current_dir = process.cwd().split("/")
    while (current_dir[current_dir.length - 1] === "http-server"){
        process.chdir('../')
        current_dir = process.cwd().split("/")
    }
}

function write_config(json){
    check_DIR()
    let data = JSON.stringify(json);
    console.log(process.cwd()+'/config.json')
    fs.writeFileSync(process.cwd()+'/config.json', data)
}

function read_config(){
    check_DIR()
    let rawdata = fs.readFileSync(process.cwd()+'/config.json');
    let json = JSON.parse(rawdata);
    console.log(json)
    return json
}


//Function to pause the code
function sleep(ms) {
    return new Promise((resolve) => {
      setTimeout(resolve, ms);
    });
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
    let result = addresses.map(a => a.Address);
    return result
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
    let addresses = await get_scanned_addresses()
    console.log(addresses)
    res.render('addresses', {addresses:addresses})
});

app.get('/run', async function(req, res) {
    console.log('Runnign')
    status = 'Running'
    console.log('Run button clicked')
    check_DIR()
    const to_run = "python3 " + process.cwd() + "/vuln-Assesment.py"
    console.log(to_run)
    exec(to_run, async (err, output) => {
        if (err){
            console.error('Could not run assesment.', err)
            status = "Error"
            console_text = "Error"
        }
        status = 'Finished'
        console_text += output
        console.log(output)
        await sleep(30000)
        status = 'Not running'
    })
    res.sendStatus(200)
});

app.get('/address_report', function(req, res){
    check_DIR()
    //http://127.0.0.1:8085/address_report?address=Test
    let address = req.query.address
    const nav_bar = fs.readFileSync(process.cwd()+'/http-server/views/partials/nav.ejs', 'utf8');
    const address_report = fs.readFileSync(process.cwd()+'/reports/'+address+'/2023-06-08.html', 'utf8');
    res.set('Content-Type', 'text/html');
    res.send(Buffer.from(nav_bar+address_report));
})

app.get('/status', function(req, res){
    res.send({"status": status})
})

app.get('/scan-settings', function(req, res){
    //http://127.0.0.1:8085/scan-settings?verbose=True&debug=True&email=True
    if (Object.keys(req.query).length === 0){
        res.send(read_config())
    }else{
        write_config(req.query)
    } 
})

app.get('/console', function(req,res){
    if (Object.keys(req.query).length === 0){
        res.send(console_text)
    }else if (req.query.clear){
        console_text = ""
    }
})

app.get('/address_list', function(req,res){
    check_DIR()
    let data = fs.readFileSync(process.cwd()+'/addresses.txt');
    console.log(data)
    res.send(data)
})

app.post('/edit_addresses', function(req, res){
    check_DIR()
    let data = req.body['addresses']
    fs.writeFileSync(process.cwd()+'/addresses.txt', data);
    res.sendStatus(200)
})

app.listen(8085, '127.0.0.1')

console.log("Waiting on port 8085")