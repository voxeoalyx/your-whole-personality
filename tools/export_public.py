"""Copy only reviewed submission files to a NEW directory; never publish or copy history."""
import argparse
from pathlib import Path, PurePosixPath
import shutil

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination',type=Path)
    args=parser.parse_args()
    dest=args.destination.resolve()
    paths=(ROOT/'public-files.txt').read_text().splitlines()
    for relative in paths:
        p=PurePosixPath(relative)
        if not relative or p.is_absolute() or '..' in p.parts or '.git' in p.parts:
            raise SystemExit('Invalid allowlist entry')
        source=ROOT/relative
        if not source.is_file() or source.is_symlink():
            raise SystemExit('Allowlisted file missing or symlink: '+relative)
    # Refuse existing targets; no accidental overwrite or inclusion of unreviewed files.
    dest.mkdir(parents=True,exist_ok=False)
    for relative in paths:
        target=dest/relative;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/relative,target)
        if relative in {'start.sh','.githooks/pre-commit'}:
            target.chmod(0o755)
    print('Prepared '+str(len(paths))+' files without Git history. Not published. Review provider-data rights before release.')

if __name__=='__main__':main()
