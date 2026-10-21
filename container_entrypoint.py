"""Initialize the mounted budget directory, then permanently drop app privileges."""
import os

if os.geteuid() != 0:
    raise SystemExit('Container bootstrap must initialize the volume before dropping privileges.')
if os.path.islink('/state'):
    raise SystemExit('The state directory must not be a symlink.')
os.chown('/state', 10001, 10001)
os.chmod('/state', 0o700)
os.setgroups([])
os.setgid(10001)
os.setuid(10001)
os.execvp('python', ['python', 'serve_public.py'])
