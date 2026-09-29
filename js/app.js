// Import the native compiled C++ binary bridge
const hardware = require('./build/Release/hardware_bridge.node');

// Direct C++ invocation from JavaScript
const currentTemp = hardware.getTemperature();
console.log(`[C++ Hardware Bridge] Current Sensor Temp: ${currentTemp}°C`);

// Capture high-speed thermal array buffer from C++
const frameBuffer = hardware.captureThermalFrame();
const thermalArray = new Float32Array(frameBuffer);

console.log(`[C++ Hardware Bridge] Recieved Thermal Frame. Buffer length: ${thermalArray.length} points.`);
