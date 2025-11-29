import Flutter
import UIKit

@main
@objc class AppDelegate: FlutterAppDelegate {
  override func application(
    _ application: UIApplication,
    didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
  ) -> Bool {
    let controller = window?.rootViewController as! FlutterViewController
    let remoteAccessChannel = FlutterMethodChannel(
      name: "com.paisaguardian/remote_access",
      binaryMessenger: controller.binaryMessenger
    )
    
    remoteAccessChannel.setMethodCallHandler { [weak self] (call, result) in
      if call.method == "detectRemoteAccess" {
        let detectionResult = self?.detectRemoteAccessApps() ?? [:]
        result(detectionResult)
      } else {
        result(FlutterMethodNotImplemented)
      }
    }
    
    GeneratedPluginRegistrant.register(with: self)
    return super.application(application, didFinishLaunchingWithOptions: launchOptions)
  }
  
  private func detectRemoteAccessApps() -> [String: Any] {
    var detectedApps: [String] = []
    let runningProcesses: [String] = []
    
    // Known remote access app bundle identifiers for iOS
    let remoteAccessBundles = [
      "com.anydesk.anydesk",
      "com.teamviewer.TeamViewerQS",
      "com.teamviewer.TeamViewer",
      "com.google.chromeremotedesktop",
      "com.microsoft.rdc.ios",
      "com.realvnc.vncviewer",
      "com.splashtop.remote",
      "com.logmein.ignition",
      "com.remotepc.viewer",
      "com.zoho.assist",
      "com.supremocontrol.supremo"
    ]
    
    let remoteAccessNames: [String: String] = [
      "com.anydesk.anydesk": "AnyDesk",
      "com.teamviewer.TeamViewerQS": "TeamViewer QuickSupport",
      "com.teamviewer.TeamViewer": "TeamViewer",
      "com.google.chromeremotedesktop": "Chrome Remote Desktop",
      "com.microsoft.rdc.ios": "Microsoft Remote Desktop",
      "com.realvnc.vncviewer": "VNC Viewer",
      "com.splashtop.remote": "Splashtop",
      "com.logmein.ignition": "LogMeIn",
      "com.remotepc.viewer": "RemotePC",
      "com.zoho.assist": "Zoho Assist",
      "com.supremocontrol.supremo": "Supremo"
    ]
    
    // Note: iOS has strict sandboxing, so we can only check for installed apps
    // via URL schemes, but we cannot directly check running processes
    // due to privacy restrictions. We'll check if these apps can be opened.
    
    for bundleId in remoteAccessBundles {
      // Create a URL scheme from bundle ID (simplified approach)
      // Most remote access apps register custom URL schemes
      let schemes = [
        "anydesk://",
        "teamviewer://",
        "chromeremotedesktop://",
        "msrdp://",
        "vnc://",
        "splashtop://",
        "logmein://",
        "remotepc://",
        "zohoassist://",
        "supremo://"
      ]
      
      // Check if URL scheme can be opened (indicates app is installed)
      for scheme in schemes {
        if let url = URL(string: scheme) {
          if UIApplication.shared.canOpenURL(url) {
            // Extract app name from scheme
            let schemeName = scheme.replacingOccurrences(of: "://", with: "")
            let matchingBundle = remoteAccessBundles.first { bundle in
              bundle.lowercased().contains(schemeName.lowercased())
            }
            if let bundle = matchingBundle, let appName = remoteAccessNames[bundle] {
              if !detectedApps.contains(appName) {
                detectedApps.append(appName)
              }
            }
          }
        }
      }
    }
    
    // iOS limitation: We cannot determine if apps are actively running
    // We can only detect if they're installed
    
    return [
      "isDetected": !detectedApps.isEmpty,
      "detectedApps": detectedApps,
      "runningProcesses": runningProcesses
    ]
  }
}

