class ForensicRouter {
    constructor() {
        this.routes = {};
        this.loadedModules = {};
        
        // Listen to hash changes or custom navigation events
        window.addEventListener('hashchange', () => this.handleRoute());
        window.addEventListener('DOMContentLoaded', () => this.handleRoute());
    }

    /**
     * Register a route path to a specific script module
     * @param {string} path - The URL hash/path (e.g., '#cockpit', '#radio')
     * @param {string} modulePath - Relative path to the JS module
     * @param {Function} initCallback - Function to call once loaded
     */
    addRoute(path, modulePath, initCallback) {
        this.routes[path] = { modulePath, initCallback };
    }

    async handleRoute() {
        const currentHash = window.location.hash || '#cockpit'; // Default route
        const route = this.routes[currentHash];

        if (!route) {
            console.warn(`[Router] Route not found: ${currentHash}`);
            return;
        }

        try {
            // Lazy-load the module only if it hasn't been loaded yet
            if (!this.loadedModules[currentHash]) {
                console.log(`[Router] Loading module for ${currentHash}...`);
                this.loadedModules[currentHash] = await import(route.modulePath);
            }

            // Execute the initialization callback with the loaded module
            if (typeof route.initCallback === 'function') {
                route.initCallback(this.loadedModules[currentHash]);
            }
        } catch (error) {
            console.error(`[Router] Failed to load module for ${currentHash}:`, error);
        }
    }
}

// ==========================================
// Usage Example for Your Forensic Modules
// ==========================================
const router = new ForensicRouter();

// 1. UI Cockpit Route
router.addRoute('#cockpit', './asset/js/ferensics/UiCoclpit.js', (module) => {
    if (module.initializeCockpit) module.initializeCockpit();
});

// 2. Radio Daemon Route
router.addRoute('#radio', './asset/js/ferensics/radioDeamon.js', (module) => {
    if (module.startRadioDaemon) module.startRadioDaemon();
});

// 3. Exit Handler & Trigger Routes (or trigger-based loading)
router.addRoute('#exit', './asset/js/ferensics/exitHandeler.js', (module) => {
    if (module.initExitHandler) module.initExitHandler();
});
