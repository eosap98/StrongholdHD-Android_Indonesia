"""Build Stronghold 1.6.6 from the compact source archive and a private backup."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parent
SOURCE_SHA256 = '4b35ac88f28f43a24de4f8758950bdcfdbd478bb107395632879373f350e9631'


def unpack_source(destination):
    bundle = ROOT/'SOURCE-BUILD.zip'
    if hashlib.sha256(bundle.read_bytes()).hexdigest() != SOURCE_SHA256:
        raise ValueError('SOURCE-BUILD.zip berubah; SHA-256 tidak cocok.')
    with zipfile.ZipFile(bundle) as archive:
        names = archive.namelist()
        manifest = json.loads(archive.read('SOURCE-MANIFEST.json'))['files']
        if len(names) != len(set(names)) or set(names) != set(manifest) | {'SOURCE-MANIFEST.json'}:
            raise ValueError('Daftar source dalam ZIP tidak cocok.')
        for name, entry in manifest.items():
            path = PurePosixPath(name)
            info = archive.getinfo(name)
            if path.is_absolute() or '..' in path.parts or '\\' in name or ':' in name or stat.S_ISLNK(info.external_attr >> 16):
                raise ValueError('Path source tidak valid: '+name)
            data = archive.read(name)
            if len(data) != entry['bytes'] or hashlib.sha256(data).hexdigest() != entry['sha256']:
                raise ValueError('Hash source tidak cocok: '+name)
            target = destination.joinpath(*path.parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    # The original preflight refers to this guide on missing prerequisites.
    shutil.copy2(ROOT/'README.md', destination/'BUILD-PC-BARU.md')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sdk', type=Path, required=True, help='Android SDK Linux dengan NDK 27.2.12479018')
    parser.add_argument('--backup-dir', type=Path, required=True, help='Folder hasil ekstraksi backup pribadi, berisi inputs/ dan private/')
    parser.add_argument('--work-root', type=Path, default=ROOT/'build/work')
    parser.add_argument('--output', type=Path, default=ROOT/'dist/Stronghold-1.6.6-Indonesia.apk')
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    backup = args.backup_dir.expanduser().resolve()
    local = ['inputs/upstream-1.0.apk', 'android/app/assets/language/catalog.json',
             'android/app/assets/language/crusader.zip', 'android/app/assets/language/stronghold.zip']
    missing = [name for name in local + ['private/signing/stronghold-rev12.keystore', 'private/signing/password.txt']
               if not (backup/name).is_file()]
    if missing:
        parser.error('Backup belum lengkap atau --backup-dir salah:\n'+'\n'.join(missing))
    work = args.work_root.expanduser().resolve()
    work.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='source-', dir=work) as temp:
        source = Path(temp)
        unpack_source(source)
        for name in local:
            target = source/name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(backup/name, target)
        command = [sys.executable, str(source/'tools/build_new_pc.py'),
            '--sdk', str(args.sdk.expanduser().resolve()), '--signing-dir', str(backup/'private/signing'),
            '--work-root', str(work), '--output', str(args.output.expanduser().resolve())]
        if args.check_only: command.append('--check-only')
        subprocess.run(command, cwd=source, check=True)


if __name__ == '__main__': main()
