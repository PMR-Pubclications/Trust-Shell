# Trust-Shell APK scaffold

This repository now contains a minimal Android application scaffold for building an APK in GitHub Actions or locally with Gradle.

## Build locally

```bash
./gradlew assembleRelease
```

## Build in CI

The project uses the standard Android Gradle plugin and will output a release APK to:

```text
app/build/outputs/apk/release/
```

## Notes

- The original mining daemon was removed from the Python runtime file so the project is suitable as an app base.
- The Android shell loads a local offline HTML page from `app/src/main/assets/www/index.html`.
- You can extend this app with secure browsing, local vault access, or embedded offline content.
