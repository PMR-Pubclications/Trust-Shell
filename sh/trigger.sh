git add .
git commit -m "Initialize Trust Secure Field Shell architecture"
git push origin main

# Tag a release to fire up the automated APK compiler
git tag v1.0.0
git push origin --tags
