# Remote Work Focus Tracker

[![Sponsor](https://img.shields.io/badge/Sponsor-GitHub%20Sponsors-ea4aaa?logo=githubsponsors)](https://github.com/sponsors/sdotwinter)

A lightweight Python CLI to help remote workers track focus sessions, distractions, and trends.

## What it does
- Log a focus session with duration and distraction count
- Generate a multi-day summary with a focus score
- Provide an AI-style suggestion based on your recent pattern
- Show today's quick snapshot

## Installation
```bash
cd /home/sean/.openclaw/workspace/app-factory-hub/projects/remote-work-focus-tracker
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage
```bash
python main.py log --minutes 50 --distractions 2 --notes "Deep work on roadmap"
python main.py today
python main.py summary --days 7
```

## Data
Session logs are stored locally in `data/sessions.json`.

## Sponsorware
This project is released as **Sponsorware**.

- You can evaluate and use it for personal/non-commercial workflows.
- For commercial/team usage and priority features, sponsor access is required.
- Suggested support tier: **$14/month**.
