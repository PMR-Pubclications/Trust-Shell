#include "TrustMainGateway.cpp" // Or include your header if split

int main() {
    std::cout << "[*] Initializing C++ Edge Defense & Gateway..." << std::endl;

    // 1. Initialize the gateway on your chosen port (e.g., port 8080 or custom port)
    TrustMainGateway gateway(8080);
    if (!gateway.initialize()) {
        std::cerr << "[-] Failed to start Trust-Main Gateway." << std::endl;
        return 1;
    }

    // 2. Accept the connection from Trust-Main (run in a dedicated background thread)
    std::thread acceptorThread([&gateway]() {
        gateway.acceptConnection();
    });
    acceptorThread.detach();

    // 3. Main processing loop (where your C++ engine processes raw data/threats)
    while (true) {
        // [Your C++ decompiler / shield-and-sword logic runs here]
        // Once a packet is cleaned and verified, dispatch the lightweight state:
        
        // std::string secureState = "{ \"status\": \"secure\", \"threats_neutralized\": 1 }";
        // gateway.dispatchToTrustMain(secureState);

        std::this_thread::sleep_for(std::chrono::milliseconds(50));
    }

    return 0;
}
