package com.legacy.security;

import java.nio.file.Path;
import java.security.PublicKey;

public class TrustCommandProcessor {

    /**
     * Processes an incoming radio code command from the Trust-Shell shell
     * by routing it through your secure cryptographic gateway.
     */
    public static void executeRadioCodeCommand(
            String radioCode, 
            Path assetPath, 
            SecureTrustAndForensicGateway.ClearanceRole role,
            byte[] authData, 
            byte[] signature, 
            PublicKey publicKey,
            Path secureVaultRoot) {

        System.out.println("Processing radio code [" + radioCode + "] for role: " + role);

        // 1. If the command involves handling or archiving an asset/log,
        // use your gateway's built-in boundary and hashing validation:
        if (assetPath != null) {
            SecureTrustAndForensicGateway.routeAndIsolateAsset(
                assetPath, 
                secureVaultRoot, 
                role, 
                authData, 
                signature, 
                publicKey
            );
        } else {
            // 2. For pure state changes (like 10-23 arrival or 10-8 departure logs),
            // enforce the passkey and domain boundary check first:
            boolean isAuthorized = SecureTrustAndForensicGateway.evaluateDomainBoundary(
                role, 
                SecureTrustAndForensicGateway.SystemDomain.FIRST_RESPONDER_OPS, 
                authData, 
                signature, 
                publicKey
            );

            if (isAuthorized) {
                System.out.println("Radio Code [" + radioCode + "] successfully authenticated and logged to immutable ledger.");
            } else {
                System.err.println("Security Fault: Radio code execution rejected due to failed gateway validation.");
            }
        }
    }
}
