const http = require('http');
const tessel = require('tessel');
const { networkInterfaces } = require('os');

const pinMap = {
    'yellow': 0,
    'green': 1,
    'red': 2,
    'blue': 3
}

const intervalMap = new Map() // map color to interval id (for clearInterval)

// Turn off all LEDs
for (const pinNo of Object.values(pinMap)) {
    tessel.port.A.pin[pinNo].output(0);
} 

const server = http.createServer(function (request, response) {
    let data = '';
    request.on('data', chunk => {
        data += chunk;
    });
    request.on('end', () => {
        parsedData = JSON.parse(data);
        console.log(`Received: ${data}`);
        processRequest(parsedData, response);
    });
});

const port = 8080;
const ip = getLocalIP();
server.listen(port);
console.log(`Listening at ${ip}:${port}`);

function processRequest(data, response) {
    for (let [color, command] of Object.entries(data)) {
        if (pinMap.hasOwnProperty(color)) {
            switch(command) {
              case 'TurnOn':
                setPin(color, 1);
                break;
              case 'TurnOff':
                setPin(color, 0);
                break;
              case 'Blink':
                blink(color);
                break;
              default:
                console.log('Command not recognized.')
            }
        } else {
            console.log(`No ${color} LED found.`)
        }
    }
    response.end();
}

function setPin(color, value) {
  stopBlinking(color);
  console.log(`Setting pin for ${color} LED to ${value}.`);
  const pin = getPinByLEDColor(color);
  pin.output(value);
}

function blink(color) {
  stopBlinking(color);
  console.log(`Making ${color} LED blink.`);
  const pin = getPinByLEDColor(color);
  const intervalID = setInterval(function(){ pin.toggle() }, 300);
  intervalMap.set(color, intervalID); // save id to map to be able to stop blinking again
}

function stopBlinking(color) {
  if (intervalMap.has(color)) {
    clearInterval(intervalMap.get(color));
  }
}

function getPinByLEDColor(color) {
    const pinNo = pinMap[color];
    const pin = tessel.port.A.pin[pinNo];
    return pin;
}

function getLocalIP() {
  const nets = networkInterfaces();
  for (const net of nets['wlan0']) {
      // Skip over non-IPv4 and internal (i.e. 127.0.0.1) addresses
      if (net.family === 'IPv4' && !net.internal) {
          return net.address;
      }
  }
}