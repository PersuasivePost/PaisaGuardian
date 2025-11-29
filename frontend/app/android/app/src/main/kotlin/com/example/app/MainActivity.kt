package com.example.app

import android.Manifest
import android.app.ActivityManager
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.content.pm.PackageManager
import android.database.Cursor
import android.net.Uri
import android.os.Build
import android.provider.Telephony
import android.telephony.SmsMessage
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel

class MainActivity : FlutterActivity() {
    private val CHANNEL = "com.paisaguardian/remote_access"
    private val SMS_CHANNEL = "com.example.app/sms"
    private val SMS_PERMISSION_CODE = 101
    
    private var smsMethodChannel: MethodChannel? = null
    private var smsReceiver: BroadcastReceiver? = null

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        
        // Remote access detection channel
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, CHANNEL).setMethodCallHandler { call, result ->
            if (call.method == "detectRemoteAccess") {
                val detectionResult = detectRemoteAccessApps()
                result.success(detectionResult)
            } else {
                result.notImplemented()
            }
        }
        
        // SMS monitoring channel
        smsMethodChannel = MethodChannel(flutterEngine.dartExecutor.binaryMessenger, SMS_CHANNEL)
        smsMethodChannel?.setMethodCallHandler { call, result ->
            when (call.method) {
                "startSmsListener" -> {
                    if (checkAndRequestSmsPermission()) {
                        startSmsListener()
                        result.success(true)
                    } else {
                        result.success(false)
                    }
                }
                "stopSmsListener" -> {
                    stopSmsListener()
                    result.success(true)
                }
                "getSmsInbox" -> {
                    if (checkSmsPermission()) {
                        val messages = getSmsInbox()
                        result.success(messages)
                    } else {
                        result.error("PERMISSION_DENIED", "SMS permission not granted", null)
                    }
                }
                "checkSmsPermission" -> {
                    result.success(checkSmsPermission())
                }
                "requestSmsPermission" -> {
                    val granted = checkAndRequestSmsPermission()
                    result.success(granted)
                }
                else -> result.notImplemented()
            }
        }
    }
    
    private fun checkSmsPermission(): Boolean {
        return ContextCompat.checkSelfPermission(this, Manifest.permission.RECEIVE_SMS) == PackageManager.PERMISSION_GRANTED &&
               ContextCompat.checkSelfPermission(this, Manifest.permission.READ_SMS) == PackageManager.PERMISSION_GRANTED
    }
    
    private fun checkAndRequestSmsPermission(): Boolean {
        if (!checkSmsPermission()) {
            ActivityCompat.requestPermissions(
                this,
                arrayOf(
                    Manifest.permission.RECEIVE_SMS,
                    Manifest.permission.READ_SMS
                ),
                SMS_PERMISSION_CODE
            )
            return false
        }
        return true
    }
    
    private fun startSmsListener() {
        if (smsReceiver != null) return
        
        smsReceiver = object : BroadcastReceiver() {
            override fun onReceive(context: Context?, intent: Intent?) {
                if (intent?.action == Telephony.Sms.Intents.SMS_RECEIVED_ACTION) {
                    val bundle = intent.extras
                    if (bundle != null) {
                        val pdus = bundle.get("pdus") as? Array<*>
                        pdus?.forEach { pdu ->
                            val format = bundle.getString("format")
                            val smsMessage = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                                SmsMessage.createFromPdu(pdu as ByteArray, format)
                            } else {
                                @Suppress("DEPRECATION")
                                SmsMessage.createFromPdu(pdu as ByteArray)
                            }
                            
                            val sender = smsMessage.displayOriginatingAddress ?: "Unknown"
                            val messageBody = smsMessage.messageBody ?: ""
                            
                            // Send to Flutter
                            runOnUiThread {
                                smsMethodChannel?.invokeMethod("onSmsReceived", mapOf(
                                    "sender" to sender,
                                    "message" to messageBody
                                ))
                            }
                        }
                    }
                }
            }
        }
        
        val filter = IntentFilter(Telephony.Sms.Intents.SMS_RECEIVED_ACTION)
        filter.priority = IntentFilter.SYSTEM_HIGH_PRIORITY
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            registerReceiver(smsReceiver, filter, RECEIVER_NOT_EXPORTED)
        } else {
            registerReceiver(smsReceiver, filter)
        }
    }
    
    private fun stopSmsListener() {
        smsReceiver?.let {
            try {
                unregisterReceiver(it)
            } catch (e: Exception) {
                // Receiver not registered
            }
            smsReceiver = null
        }
    }
    
    private fun getSmsInbox(): List<Map<String, String>> {
        val messages = mutableListOf<Map<String, String>>()
        val uri = Uri.parse("content://sms/inbox")
        
        try {
            val cursor: Cursor? = contentResolver.query(
                uri,
                arrayOf("_id", "address", "body", "date"),
                null,
                null,
                "date DESC LIMIT 50"
            )
            
            cursor?.use {
                val addressIndex = it.getColumnIndex("address")
                val bodyIndex = it.getColumnIndex("body")
                val dateIndex = it.getColumnIndex("date")
                
                while (it.moveToNext()) {
                    val address = if (addressIndex >= 0) it.getString(addressIndex) ?: "" else ""
                    val body = if (bodyIndex >= 0) it.getString(bodyIndex) ?: "" else ""
                    val date = if (dateIndex >= 0) it.getString(dateIndex) ?: "" else ""
                    
                    messages.add(mapOf(
                        "sender" to address,
                        "message" to body,
                        "date" to date
                    ))
                }
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
        
        return messages
    }
    
    override fun onDestroy() {
        stopSmsListener()
        super.onDestroy()
    }

    private fun detectRemoteAccessApps(): Map<String, Any> {
        val detectedApps = mutableListOf<String>()
        val runningProcesses = mutableListOf<String>()
        
        // List of known remote access app package names
        val remoteAccessPackages = listOf(
            "com.anydesk.anydeskandroid",
            "com.teamviewer.teamviewer.market.mobile",
            "com.teamviewer.quicksupport.market",
            "com.google.chromeremotedesktop",
            "com.microsoft.rdc.android",
            "com.realvnc.viewer.android",
            "com.splashtop.remote",
            "com.logmein.ignitionpro.android",
            "com.remotepc.viewer",
            "com.zoho.assist",
            "com.aeroadmin",
            "com.ammyy.admin",
            "com.ultraviewer",
            "com.supremo",
            "com.rsupport.rs.activity"
        )

        val remoteAccessNames = mapOf(
            "com.anydesk.anydeskandroid" to "AnyDesk",
            "com.teamviewer.teamviewer.market.mobile" to "TeamViewer",
            "com.teamviewer.quicksupport.market" to "TeamViewer QuickSupport",
            "com.google.chromeremotedesktop" to "Chrome Remote Desktop",
            "com.microsoft.rdc.android" to "Microsoft Remote Desktop",
            "com.realvnc.viewer.android" to "VNC Viewer",
            "com.splashtop.remote" to "Splashtop",
            "com.logmein.ignitionpro.android" to "LogMeIn",
            "com.remotepc.viewer" to "RemotePC",
            "com.zoho.assist" to "Zoho Assist",
            "com.aeroadmin" to "AeroAdmin",
            "com.ammyy.admin" to "Ammyy Admin",
            "com.ultraviewer" to "UltraViewer",
            "com.supremo" to "Supremo",
            "com.rsupport.rs.activity" to "RemoteView"
        )

        try {
            val activityManager = getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager
            val runningApps = activityManager.runningAppProcesses

            if (runningApps != null) {
                for (processInfo in runningApps) {
                    val processName = processInfo.processName
                    runningProcesses.add(processName)
                    
                    // Check if any remote access app is running
                    for (packageName in remoteAccessPackages) {
                        if (processName.contains(packageName, ignoreCase = true)) {
                            val appName = remoteAccessNames[packageName] ?: packageName
                            if (!detectedApps.contains(appName)) {
                                detectedApps.add(appName)
                            }
                        }
                    }
                }
            }

            // Also check installed packages
            val packageManager = packageManager
            for (packageName in remoteAccessPackages) {
                try {
                    val packageInfo = packageManager.getPackageInfo(packageName, 0)
                    val appName = remoteAccessNames[packageName] ?: packageName
                    // Only add if app is installed (not necessarily running)
                    if (packageInfo != null && !detectedApps.contains(appName)) {
                        // Check if app is in foreground/background
                        val isRunning = runningProcesses.any { it.contains(packageName, ignoreCase = true) }
                        if (isRunning) {
                            detectedApps.add(appName)
                        }
                    }
                } catch (e: Exception) {
                    // Package not installed, ignore
                }
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }

        return mapOf(
            "isDetected" to (detectedApps.isNotEmpty()),
            "detectedApps" to detectedApps,
            "runningProcesses" to runningProcesses.take(50) // Limit to 50 processes
        )
    }
}
