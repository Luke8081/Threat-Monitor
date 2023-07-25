var express = require('express');
var fs = require('fs');
const path = require('path')
const router = express.Router()
const { exec } = require('child_process');
const { type } = require('os');
const sqlite = require('sqlite3').verbose()
const readline = require('readline');

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
    console.log(process.cwd()+'/config/config.json')
    fs.writeFileSync(process.cwd()+'/config/config.json', data)
}

function read_config(){
    check_DIR()
    let rawdata = fs.readFileSync(process.cwd()+'/config/config.json');
    let json = JSON.parse(rawdata);
    return json
}


function get_report_files(address){
    check_DIR()
    var files = fs.readdirSync(process.cwd()+'/reports/'+address);
    //Remove .html off dates. Also remove Json from list
    files = files.map(e => e.replace('.html', '')).filter(e => e !== 'JSON');
    return files
}


function get_recent_date(address){
    let files = get_report_files(address)
    //Get most recent date. Converts to date format for comparing
    var recent_date = new Date(Math.max(...files.map(e => new Date(e))));

    //Convert it back to files format
    recent_date = recent_date.toISOString().split('T')[0] + '.html'
    return recent_date
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

app.get('/alerts', async function(req, res){
    const alerts = await get_alerts()
    res.setHeader('Content-Type', 'application/json');
    res.send(JSON.stringify(alerts))
})

app.get('/', function(req, res) {
    check_DIR()

    var API_key = process.env.CRONITOR_API_KEY
    res.render("home")
});

app.get('/addresses', async function(req, res) {
    res.render('addresses')
});

app.get('/run', async function(req, res) {
    status = 'Running'
    check_DIR()
    const to_run = "python3 " + process.cwd() + "/vuln-Assesment.py"
    exec(to_run, async (err, output) => {
        if (err){
            console.error('Could not run assesment.', err)
            status = "Error"
            console_text += output
        }
        status = 'Finished'
        console_text += output
        console.log(output)
        await sleep(30000)
        status = 'Not running'
    })
    res.sendStatus(200)
});

app.get('/address_report', async function(req, res){
    check_DIR()
    //http://127.0.0.1:8085/address_report?address=Test
    let address = req.query.address

    //Send the addresses on request
    if (address == "get_addresses"){
        let addresses = await get_scanned_addresses()
        var files = fs.readdirSync(process.cwd()+'/reports/');
        addresses = addresses.filter(element => files.includes(element));
        res.setHeader('Content-Type', 'application/json');
        res.send(JSON.stringify(addresses))
        return
    }

    //Get the report for address
    let recent_date = get_recent_date(address)
    const nav_bar = fs.readFileSync(process.cwd()+'/http-server/views/partials/nav.ejs', 'utf8');
    const address_report = fs.readFileSync(process.cwd()+'/reports/'+address+'/'+recent_date, 'utf8');
    res.set('Content-Type', 'text/html');
    res.send(Buffer.from(nav_bar+address_report));
})

app.get('/address_report_history', function(req, res){
    check_DIR()
    let address = req.query.address
    if (Object.keys(req.query).length == 2){
        let date = req.query.date
        const nav_bar = fs.readFileSync(process.cwd()+'/http-server/views/partials/nav.ejs', 'utf8');
        const address_report = fs.readFileSync(process.cwd()+'/reports/'+address+'/'+date+'.html', 'utf8');
        res.set('Content-Type', 'text/html');
        res.send(Buffer.from(nav_bar+address_report));
    }else{
        console.log('Get report history')
        //http://127.0.0.1:8085/address_report_history?address=public-firing-range.appspot.com
        let files = get_report_files(address)
        res.setHeader('Content-Type', 'application/json');
        res.send(JSON.stringify(files))
    }
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
    let data = fs.readFileSync(process.cwd()+'/config/addresses.txt');
    res.send(data)
})

app.post('/edit_addresses', function(req, res){
    check_DIR()
    let data = req.body['addresses']
    try{
        fs.writeFileSync(process.cwd()+'/config/addresses.txt', data);
        res.sendStatus(200)
    }catch(err){
        console.error(err)
        res.sendStatus(500)
    }
})
app.get('/scan_log', function(req, res){
    check_DIR()
    if (Object.keys(req.query).length === 0){
        let data = fs.readFileSync(process.cwd()+'/reports/scan_log.txt');
        console_text += data
        res.send(data)
    }else if (req.query.recent){

        const rl = readline.createInterface({
            input: fs.createReadStream(process.cwd()+'/reports/scan_log.txt'),
            crlfDelay: Infinity
        });

        let last5Rows = []
        rl.on('line', (line) => {
            last5Rows.push(line);
            if (last5Rows.length > 5) {
              last5Rows.shift(); // Remove the first element when the array has more than 5 elements
            }
        })
        rl.on('close', () => {
            console.log('Last 5 rows:');
            console.log(last5Rows)
            let separatorIndex = last5Rows.indexOf('Number')
            console.log(separatorIndex)
            const data = last5Rows.slice(separatorIndex + 1)
            console.log(data)

        })
        
    } 
})

app.listen(8085, '127.0.0.1')

console.log("Waiting on port 8085")