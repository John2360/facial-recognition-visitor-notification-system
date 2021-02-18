var express = require('express');
var cors = require('cors');
var app = express();
var path = require('path');

app.use(cors());
app.options('*', cors());  // enable pre-flight
app.use('/', express.static(path.join(__dirname, 'public'), {
  setHeaders: function setHeaders(res, path, stat) {
    res.header('Access-Control-Allow-Origin', '*');
    res.header('Access-Control-Allow-Methods', 'GET');
    res.header('Access-Control-Allow-Headers', 'Content-Type');
  }
}));

// viewed at http://localhost:8080

app.listen(8080);