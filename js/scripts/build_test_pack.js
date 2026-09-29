const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

function buildAccountTestPack(accountConfig) {
  const rootDir = path.join(__dirname, '..');
  const packagePath = path.join(rootDir, 'package.json');
  const packageJson = JSON.parse(fs.readFileSync(packagePath, 'utf8'));

  // 1. Read AI summary or fallback to Git log
  const summaryPath = path.join(rootDir, '.github/commit_summary.txt');
  let releaseDescription = '';

  if (fs.existsSync(summaryPath)) {
    releaseDescription = fs.readFileSync(summaryPath, 'utf8');
  } else {
    const gitLog = execSync('git log -n 5 --pretty=format:"* %s (%h)"').toString();
    releaseDescription = `Automated Test Pack Provisioning.\n\nChanges Included:\n${gitLog}`;
  }

  // 2. Embed custom fields into test pack package.json
  packageJson.description = releaseDescription.split('\n')[0];
  packageJson.testPackMetadata = {
    provisionedFor: accountConfig.accountId,
    accountType: accountConfig.type || "TEST_ACCOUNT",
    releaseNotes: releaseDescription,
    timestamp: new Date().toISOString()
  };

  fs.writeFileSync(packagePath, JSON.stringify(packageJson, null, 2));

  // 3. Create a dedicated release notes file inside the package root
  const testNotesPath = path.join(rootDir, 'TEST_PACK_NOTES.md');
  const notesContent = `# Test Package Overview (${accountConfig.accountId})\n` +
                       `**Generated:** ${new Date().toUTCString()}\n\n` +
                       `## Features & Changes in this Build\n${releaseDescription}\n`;
  
  fs.writeFileSync(testNotesPath, notesContent);

  // 4. Bundle into tarball using npm pack
  console.log(`[Test Pack Builder] Packing test archive for ${accountConfig.accountId}...`);
  const tarballName = execSync('npm pack', { cwd: rootDir }).toString().trim();

  // 5. Rename/Move tarball into account test release directory
  const outputDir = path.join(rootDir, 'dist/test_packs');
  fs.mkdirSync(outputDir, { recursive: true });

  const finalTarballPath = path.join(outputDir, `${accountConfig.accountId}_test_pack.tgz`);
  fs.renameSync(path.join(rootDir, tarballName), finalTarballPath);

  console.log(`[Test Pack Ready] Archive created at: ${finalTarballPath}`);
  return finalTarballPath;
}

// Execution for test account provisioning
buildAccountTestPack({
  accountId: "TEST_USER_9727",
  type: "Initial_Onboarding_Pack"
});
