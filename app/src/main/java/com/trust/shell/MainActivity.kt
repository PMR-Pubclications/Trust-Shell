package com.trust.shell

import android.annotation.SuppressLint
import android.os.Bundle
import android.webkit.JavascriptInterface
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        webView = WebView(this)
        setContentView(webView)

        val settings: WebSettings = webView.settings
        settings.javaScriptEnabled = true
        settings.domStorageEnabled = true
        settings.allowFileAccess = true
        settings.mediaPlaybackRequiresUserGesture = false

        // Bridge JavaScript calls to native Android code
        webView.addJavascriptInterface(WebAppInterface(), "AndroidInterface")

        webView.webViewClient = WebViewClient()
        
        // Load local asset shell entry point
        webView.loadUrl("file:///android_asset/www/index.html")
    }

    inner class WebAppInterface {
        @JavascriptInterface
        fun startMiningService() {
            // Native hook triggered once user passes agreement
            // Initialize background hashing or background service here
        }
    }

    override fun onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack()
        } else {
            super.onBackPressed()
        }
    }
}
