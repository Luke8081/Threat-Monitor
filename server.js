var http = require('http')
var fs = require('fs')
http.createServer(function (req, res) {
    fs.readFile('home.html', funtion(err, data){
        res.writeHead(200, {'Content-Type': 'text/html'});
        res.write(data)
        return res.end()
    })
}).listen(8081);