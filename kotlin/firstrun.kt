val sharedPref = context.getSharedPreferences("AppSettings", Context.MODE_PRIVATE)
val isFirstRun = sharedPref.getBoolean("isFirstRun", true)

if (isFirstRun) {
    showHardwarePermissionDialog()
}
