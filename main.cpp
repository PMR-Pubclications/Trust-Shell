#include "SystemBootstrap.hpp"

int main(int argc, char* argv[]) {
    // Define relative or environment-resolved paths for your multi-repo workspace
    fs::path baseDir = fs::current_path();
    
    SystemBootstrap::SystemPaths paths;
    paths.trustMainRoot  = baseDir.parent_path() / "Trust-Main";
    paths.trustShellRoot = baseDir; // Running from Trust-Shell context
    paths.avEngineRoot   = baseDir.parent_path() / "AudioVideoEngine-CPP";

    // Run independent diagnostic bootstrap sequence
    if (!SystemBootstrap::InitializeAndVerifySystem(paths)) {
        // Exit early if diagnostic audit fails
        return 1;
    }

    // Proceed with Trust-Shell and AudioVideoEngine initialization...
    std::cout << "[Trust-Shell] Initializing operational runtime...\n";
    return 0;
}
