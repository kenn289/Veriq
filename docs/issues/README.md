# Generated issues

This folder contains generated issue markdown files extracted from `docs/user_stories.md` for stories marked `Priority: High`.

Run `python scripts/generate_issues_from_stories.py` to regenerate these files locally.

To create GitHub issues automatically, run the same script with `--create-remote` and provide a `GITHUB_TOKEN` with `repo` scope or run the `.github/workflows/create_issues_from_stories.yml` workflow via the Actions tab.
