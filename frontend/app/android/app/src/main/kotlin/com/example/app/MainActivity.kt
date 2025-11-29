package com.example.app

import android.app.ActivityManager
import android.content.Context
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel

class MainActivity : FlutterActivity() {
    private val CHANNEL = "com.paisaguardian/remote_access"

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, CHANNEL).setMethodCallHandler { call, result ->
            if (call.method == "detectRemoteAccess") {
                val detectionResult = detectRemoteAccessApps()
                result.success(detectionResult)
            } else {
                result.notImplemented()
            }
        }
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
