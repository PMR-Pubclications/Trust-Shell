package com.pmr.trustshell.network

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.BufferedReader
import java.io.InputStreamReader
import java.net.Socket

class TrustMainClientConnector(private val serverIp: String, private val port: Int) {

    suspend fun startListening(onStateUpdate: (String) -> Unit) = withContext(Dispatchers.IO) {
        try {
            val socket = Socket(serverIp, port)
            val reader = BufferedReader(InputStreamReader(socket.getInputStream()))

            while (true) {
                val payload = reader.readLine() ?: break
                // Instantly pass pre-digested payload to the UI thread
                withContext(Dispatchers.Main) {
                    onStateUpdate(payload)
                }
            }
        } catch (e: Exception) {
            // Handle reconnection / dropped tunnel protocol
        }
    }
}
