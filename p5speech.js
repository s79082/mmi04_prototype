// A2Z F18
// Daniel Shiffman
// http://shiffman.net/a2z
// https://github.com/shiffman/A2Z-F187

// Speech Recognition on Edge Browser

// Speech Object
let speech;

// If you want to try partial recognition (faster, less accurate)
const interimResults = true; 

const lang = "es-US";

const socket = new WebSocket('ws://localhost:8080');

// Connection opened
socket.addEventListener('open', function (event) {
    socket.send('Hello Server soos!');
});

// Listen for messages
socket.addEventListener('message', function (event) {
    console.log('Message from server ', event.data);
});

sendMsg = (msg) => {
  if (socket.readyState === WebSocket.OPEN) {
    socket.send(msg)
  }
}

function setup() {
  noCanvas();
  // Create a Speech Recognition object with callback
  speechRec = new p5.SpeechRec(lang, gotSpeech);
  // "Continuous recognition" (as opposed to one time only)
  let continuous = true;
  
  // This must come after setting the properties
  speechRec.start(continuous, interimResults);

  // DOM element to display results
  let output = select('#speech');

  // Speech recognized event
  function gotSpeech() {
    // Something is there
    // Get it as a string, you can also get JSON with more info
    console.log(speechRec);
    if (speechRec.resultValue) {
      let said = speechRec.resultString;
      // Show user
      output.html(said);
      sendMsg(said);
    }
  }
}
