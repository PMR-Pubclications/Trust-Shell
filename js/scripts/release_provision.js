const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

function provisionAccountPackage(accountConfig) {
  const packagePath = path.join(__dirname, '../package.json');
  const packageJson = JSON.parse(fs.readFileSync(packagePath, 'utf8'));

  // 1. Fetch recent commit descriptions automatically
  console.log('[Provisioning] Reading commit history for package release...');
  const gitLog = execSync('git log -n 5 --pretty=format:"* %s (%h)"').toString();

  // 2. Read AI-generated summary if available, otherwise fallback to Git log
  const summaryPath = path.join(__dirname, '../.github/commit_summary.txt');
  let releaseDescription = '';

  if (fs.existsSync(summaryPath)) {
    releaseDescription = fs.readFileSync(summaryPath, 'utf8');
  } else {
    releaseDescription = `Initial Release provisioning for ${accountConfig.accountId}.\n\nRecent Changes:\n${gitLog}`;
  }

  // 3. Inject auto-generated metadata directly into package.json
  packageJson.description = releaseDescription.split('\n')[0]; // First line for main description
  packageJson.releaseNotes = releaseDescription;               // Full breakdown in custom property
  packageJson.provisionedFor = accountConfig.accountId;
  packageJson.provisionedAt = new Date().toISOString();

  // 4. Save updated manifest back to disk
  fs.writeFileSync(packagePath, JSON.stringify(packageJson, null, 2));
  console.log(`[Provisioning] Updated package.json for ${accountConfig.accountId}`);

  // 5. Append entry to local CHANGELOG.md included in the package
  const changelogPath = path.join(__dirname, '../CHANGELOG.md');
  const changelogEntry = `\n## Release v${packageJson.version} - ${accountConfig.accountId}\n*Date: ${new Date().toLocaleDateString()}*\n\n${releaseDescription}\n\n---`;
  
  fs.appendFileSync(changelogPath, changelogEntry);
  console.log('[Provisioning] Appended release summary to CHANGELOG.md');
}

// Example account setup execution
provisionAccountPackage({
  accountId: "USR_CLIENT_9727",
  accountType: "Initial_Setup"
});
