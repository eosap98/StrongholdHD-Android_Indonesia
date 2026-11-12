# Stronghold 1.6.6 Indonesia

## Build

Gunakan Linux x86_64 atau Ubuntu di WSL2. Pasang Python 3.11+, JDK 17+,
XZ 5.4+, binutils/readelf, dan Android SDK untuk Linux:

```sh
sudo apt update
sudo apt install python3 python3-venv openjdk-17-jdk build-essential binutils xz-utils unzip
```

Pasang [Android SDK Command-line Tools untuk Linux](https://developer.android.com/studio#command-line-tools-only)
ke `$HOME/Android/Sdk/cmdline-tools/latest`, kemudian:

```sh
export ANDROID_HOME="$HOME/Android/Sdk"
"$ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager" --licenses
"$ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager" \
  "platforms;android-36" "build-tools;36.0.0" "ndk;27.2.12479018"
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-build.txt
```

Ekstrak backup pribadi `Stronghold-1.6.6-Backup-Build-PC-Baru.zip` ke folder
terpisah. Pilih direktori hasil ekstraksi yang berisi `inputs/`, `android/`,
dan `private/` sebagai `--backup-dir`:

```sh
.venv/bin/python build.py --sdk "$ANDROID_HOME" \
  --backup-dir /lokasi/Stronghold-1.6.6-Backup-Build-PC-Baru --check-only
.venv/bin/python build.py --sdk "$ANDROID_HOME" \
  --backup-dir /lokasi/Stronghold-1.6.6-Backup-Build-PC-Baru
```

Jika tanpa internet, dependency Python dapat dipasang dari
`private/wheels` dalam backup menggunakan opsi pip
`--no-index --find-links /lokasi/backup/private/wheels`.

APK keluar di `dist/Stronghold-1.6.6-Indonesia.apk`, beserta checksum dan
laporan verifikasi. Output yang sudah ada tidak ditimpa; pilih nama baru
dengan `--output dist/build-baru.apk`. Untuk memindahkan file kerja ke drive
lain, gunakan `--work-root /lokasi/drive-lain/stronghold-build`.

Build memverifikasi arsip source, baseline upstream, input lokal, signature,
JNI dan alignment 16 KB. Tidak memakai emulator atau menjalankan game.
Ini memakai jalur patch native yang sama dengan rilis 1.6.6; seluruh source
mesin hasil konversi tidak disertakan. Source dapat dibaca dengan membuka
`SOURCE-BUILD.zip`; versi lengkap untuk pengembangan ada di backup pribadi.
