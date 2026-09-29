// authenticatedRadioListener.js

// 1. Device Profile (Unique to the device running this script)
const DEVICE_CONFIG = {
  deviceId: "UNIT_MOBILE_01",
  authorizedSpeakerId: "USER_VOICE_PRINT_9727", // Stored biometric voice embedding/hash
  minConfidenceScore: 0.85 // Threshold for voice print matching (85% similarity)
};

// 2. Radio Code Registry mapped to internal app triggers
const radioCodeRegistry = new Map([
  ["10-33", { category: "Police", action: "EXECUTE_EMERGENCY_LOCKDOWN" }],
  ["10-70", { category: "Fire", action: "TRIGGER_SCENE_RECORDING" }],
  ["10-97", { category: "Police", action: "INITIALIZE_CHAIN_OF_CUSTODY_LOG" }]
]);

/**
 * Main handler for incoming audio streams captured from the radio/mic.
 * @param {Object} audioPayload - Raw audio buffer and metadata
 */
async function processAudibleRadioCommand(audioPayload) {
  const { audioBuffer, timestamp } = audioPayload;

  console.log(`[Audio Detected] Processing broadcast at ${timestamp}...`);

  // Step 1: Extract Spoken Code and Speaker Biometrics
  const transcript = await transcribeAudio(audioBuffer); // Speech-to-Text
  const voiceAnalysis = await verifySpeakerIdentity(audioBuffer); // Voice Print Matching

  console.log(`[STT Transcript]: "${transcript}"`);
  console.log(`[Voice Print Match Score]: ${(voiceAnalysis.confidence * 100).toFixed(1)}% for Speaker: ${voiceAnalysis.detectedSpeakerId}`);

  // Step 2: Verify Device Ownership / Voice Matching
  if (voiceAnalysis.detectedSpeakerId !== DEVICE_CONFIG.authorizedSpeakerId || voiceAnalysis.confidence < DEVICE_CONFIG.minConfidenceScore) {
    console.warn(`[REJECTED] Voice print does not match Device ${DEVICE_CONFIG.deviceId}. Action denied.`);
    return;
  }

  // Step 3: Match Spoken Code to Action
  const detectedCode = extractRadioCode(transcript);

  if (!detectedCode || !radioCodeRegistry.has(detectedCode)) {
    console.log(`[Ignored] No recognized radio code in spoken audio: "${transcript}"`);
    return;
  }

  const mapping = radioCodeRegistry.get(detectedCode);
  console.log(`[AUTHENTICATED] Spoken code ${detectedCode} matches Device Authorized Voice. Executing: ${mapping.action}`);

  // Step 4: Execute Action
  executeAppAction(mapping.action, timestamp);
}

// --- Helper Functions & Mock Hardware Interfaces ---

function extractRadioCode(text) {
  // Matches codes like "10-33", "10 33", or "Ten Thirty-Three"
  const match = text.match(/\b10[- ]?\d{2}\b/);
  return match ? match[0].replace(" ", "-") : null;
}

function executeAppAction(action, timestamp) {
  switch (action) {
    case "EXECUTE_EMERGENCY_LOCKDOWN":
      console.log(`>> APP ACTION: Emergency lockdown triggered on ${DEVICE_CONFIG.deviceId}.`);
      break;
    case "TRIGGER_SCENE_RECORDING":
      console.log(`>> APP ACTION: Forensic recording initialized on ${DEVICE_CONFIG.deviceId}.`);
      break;
    case "INITIALIZE_CHAIN_OF_CUSTODY_LOG":
      console.log(`>> APP ACTION: Signing chain-of-custody log on ${DEVICE_CONFIG.deviceId}.`);
      break;
    default:
      console.log(`>> APP ACTION: Unknown action ${action}`);
  }
}

// Mock AI/Biometric Processing (Replace with actual engine like Vosk/Whisper & Resemblyzer)
async function transcribeAudio(buffer) {
  return "Officer requesting 10-33 emergency"; 
}

async function verifySpeakerIdentity(buffer) {
  // Simulates speaker verification against the local device stored voice template
  return {
    detectedSpeakerId: "USER_VOICE_PRINT_9727",
    confidence: 0.92
  };
}

module.exports = { processAudibleRadioCommand, DEVICE_CONFIG };
