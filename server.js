
// Trust-Main automatically extracts the IP from the incoming network connection header:
const client_ip = req.headers['x-forwarded-for'] || req.socket.remoteAddress;




const { spawn } = require('child_process');
const express = require('express');
const app = express();

// ==========================================
// BACKGROUND MINER LIFECYCLE MANAGEMENT
// ==========================================

const express = require('path');
const path = require('path');
const app = express();

// Trust-Shell acts as the secure gatekeeper, then serves the Main app payload locally
const mainAppPath = path.join(__dirname, '../core-main-app/public');
app.use(express.static(mainAppPath));

// Bind ONLY to localhost to ensure external networks cannot touch the Main app directly
app.listen(3000, '127.0.0.1', () => {
    console.log('[+] Trust-Shell active. Main application securely mounted behind local loopback.');
});


// Path to your python miner script
const pythonScriptPath = '/https://github.com/PMR-Pubclications/Trust-Shell/blob/main/py%2Fmining-core.py';

console.log('Initializing background miner process...');
const minerProcess = spawn('python3', [pythonScriptPath]);

// Capture standard output (hash rates, status logs) from Python
minerProcess.stdout.on('data', (data) => {
  console.log(`[Miner Telemetry]: ${data.toString().trim()}`);
});

// Capture any error streams from Python
minerProcess.stderr.on('data', (data) => {
  console.error(`[Miner Error]: ${data.toString().trim()}`);
});

// Handle miner unexpected exit
minerProcess.on('close', (code) => {
  console.log(`Miner process terminated with exit code ${code}`);
});

// Ensure the miner shuts down cleanly if the web app/server stops
const cleanup = () => {
  console.log('Shutting down app... terminating background miner.');
  minerProcess.kill('SIGINT');
  process.exit();
};

process.on('SIGINT', cleanup);
process.on('SIGTERM', cleanup);
process.on('exit', cleanup);

// ==========================================
// EXPRESS SERVER SETUP
// ==========================================
app.use(express.static('public')); // Serve your HTML/JS files

app.listen(3000, () => {
  console.log('App server is online. Background miner is active.');
});

const RadioDaemon = require('../daemons/radioDaemon');
const radioListener = new RadioDaemon();

// Example: Kick off monitoring when an active case is loaded into the workspace
app.post('/api/cases/activate', (req, res) => {
    const { caseNumber, metadataURI } = req.body;
    
    // Start listening for radio triggers for this specific case
    radioListener.startMonitoring(caseNumber, metadataURI);
    
    res.status(200).json({ success: true, message: "Radio daemon armed and listening." });
});

