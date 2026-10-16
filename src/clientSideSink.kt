import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.BufferedReader
import java.io.InputStreamReader
import java.net.Socket

class TrustMainReceiver(private val host: String, private val port: Int) {

    suspend fun connectAndListen(onStateReceived: (String) -> Unit) = withContext(Dispatchers.IO) {
        try {
            val socket = Socket(host, port)
            val reader = BufferedReader(InputStreamReader(socket.getInputStream()))

            while (true) {
                val payload = reader.readLine() ?: break
                // Hand the pre-processed, lightweight payload directly to the shell UI
                withContext(Dispatchers.Main) {
                    onStateReceived(payload)
                }
            }
        } catch (e: Exception) {
            // Handle reconnection / dropped secure tunnel logic
        }
    }
}
