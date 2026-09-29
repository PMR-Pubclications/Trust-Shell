const hardwareBridge = require('./asset/js/hardwareBridge');

function initializeShell() {
  console.log('[Trust-Shell] Initializing hardware layer...');

  if (hardwareBridge.isAvailable()) {
    const temp = hardwareBridge.getTemperature();
    console.log(`[Hardware] Thermal Sensor Active. Ambient Temp: ${temp}°C`);

    const thermalData = hardwareBridge.captureThermalFrame();
    if (thermalData) {
      console.log(`[Hardware] Thermal Frame Captured. Matrix Size: ${thermalData.length} points.`);
    }
  } else {
    console.warn('[Hardware] Running in fallback mode without native C++ bindings.');
  }
}

initializeShell();
