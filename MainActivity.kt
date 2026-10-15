package org.trust.forensicshell

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.trust.forensicshell.databinding.ActivityMainBinding

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Initialize View Binding
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // Trigger background operations safely without blocking UI
        runBackgroundOperations()
    }

    private fun runBackgroundOperations() {
        // Runs heavy tasks on a background I/O thread pool
        lifecycleScope.launch(Dispatchers.IO) {
            // TODO: Perform your background network requests, file reading, or telemetry logging here
            
            // Switches back to the main UI thread to update views safely
            withContext(Dispatchers.Main) {
                // TODO: Update your UI elements safely here
                // e.g., binding.statusTextView.text = "Connected"
            }
        }
    }
}
