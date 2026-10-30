# Resume on a Mac

The repository is private. Sign in as `voxeoalyx` or another explicitly granted collaborator. Credentials are deliberately absent from Git; obtain the existing Qloo/NVIDIA keys from your password manager or transfer them privately from the laptop. Do not paste them into chat or shell command arguments.

## First setup

Install Git, Python 3.10+ and Node 18+ (Node is for tests only). If Homebrew is already installed:

```sh
brew install git python node gh
gh auth login --hostname github.com --git-protocol https --web
gh auth setup-git
git clone https://github.com/voxeoalyx/your-whole-personality.git
cd your-whole-personality
python3 -m venv .venv
source .venv/bin/activate
cp .env.example .env
chmod 600 .env
nano .env
```

Fill only the blank `QLOO_API_KEY` and `NVIDIA_API_KEY` fields; keep the documented defaults unless your account requires different ones. Save with Ctrl+O, Enter, then Ctrl+X. You can leave keys blank to use recorded play. There is no package-install step. Without Homebrew, use the official Python, Node and GitHub CLI installers, then start at `gh auth login` above.

```sh
git config core.hooksPath .githooks
python -m unittest discover -s tests -v
node --test tests/*.test.js
python tools/audit_repository.py --history
python server.py
```

Open http://127.0.0.1:8765 in Safari or Chrome. Ctrl+C stops the server. For another port use `python server.py --port 8766`. Live picks need Qloo; the adaptive investigator also needs NVIDIA. No ChatGPT subscription/model access is assumed.

## Subsequent development

```sh
cd your-whole-personality
git pull --ff-only
source .venv/bin/activate
python server.py
```

Before your first commit, configure your own Git name/email (`git config user.name "Your Name"` and `git config user.email "YOUR_GITHUB_NOREPLY_EMAIL"`). Optional hooks are not automatically enabled by cloning. Run both test commands and the audit before pushing. Do not force-add env files, caches or new session captures. Review raw research additions for credentials and participant information first.

Read [PROJECT_STATUS.md](PROJECT_STATUS.md), [README.md](README.md), and [research/ARCHIVE.md](research/ARCHIVE.md) before changing behavior. Deployment is documented in [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md). The repository carries the saved research; no laptop directory or previous checkout is needed.

### Identity research extension

No new dependencies, database, API key or hosting service is needed. Restart the Python server after updating: its explicit static allowlist now includes `identity.js` and `research-schema.js`. Reload the browser. The optional question is after the verdict; research uses a local, consent-gated export. Do not configure automatic research ingestion. See `docs/IDENTITY_RESEARCH.md` for privacy and schema rules.

The example and server default use `nvidia/nemotron-3.5-lightning-30b-a3b`, validated against the game action schema after the prior Super endpoint timed out during release checks. Keep `NVIDIA_MODEL` configurable; provider availability and public-use permissions require separate confirmation.
