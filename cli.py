from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from datetime import date, datetime
from pathlib import Path
from typing import List

DATA_DIR = Path(__file__).parent / "data"
SESSIONS_FILE = DATA_DIR / "sessions.json"


@dataclass
class FocusSession:
    started_at: str
    minutes: int
    distraction_count: int
    notes: str = ""

    @property
    def focus_score(self) -> float:
        penalty = self.distraction_count * max(2, min(8, self.minutes // 10))
        return float(max(0, 100 - penalty))


def _ensure_storage() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not SESSIONS_FILE.exists():
        SESSIONS_FILE.write_text("[]", encoding="utf-8")


def _load_sessions() -> List[FocusSession]:
    _ensure_storage()
    raw = json.loads(SESSIONS_FILE.read_text(encoding="utf-8"))
    return [FocusSession(**item) for item in raw]


def _save_sessions(sessions: List[FocusSession]) -> None:
    payload = [asdict(s) for s in sessions]
    SESSIONS_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def cmd_log(args: argparse.Namespace) -> int:
    sessions = _load_sessions()
    session = FocusSession(
        started_at=datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        minutes=args.minutes,
        distraction_count=args.distractions,
        notes=args.notes or "",
    )
    sessions.append(session)
    _save_sessions(sessions)
    print("✅ Session logged")
    print(f"Minutes: {session.minutes}")
    print(f"Distractions: {session.distraction_count}")
    print(f"Focus score: {session.focus_score:.1f}")
    return 0


def _suggestion(avg_distractions: float, avg_score: float) -> str:
    if avg_score >= 85 and avg_distractions <= 1:
        return "Strong focus streak. Keep your current routine and protect your top focus hours."
    if avg_distractions >= 4:
        return "High interruption load. Try 25-minute focus blocks and silence non-critical notifications."
    if avg_score < 70:
        return "Focus is slipping. Start each block with one clear task and a visible timer."
    return "Good baseline. Reduce context switching by batching chat/email checks every 45-60 minutes."


def cmd_summary(args: argparse.Namespace) -> int:
    sessions = _load_sessions()
    cutoff = datetime.utcnow().date().toordinal() - args.days

    filtered: List[FocusSession] = []
    for s in sessions:
        try:
            d = datetime.fromisoformat(s.started_at.replace("Z", "")).date().toordinal()
        except ValueError:
            continue
        if d >= cutoff:
            filtered.append(s)

    if not filtered:
        print("No sessions found in selected range.")
        return 0

    total_minutes = sum(s.minutes for s in filtered)
    total_sessions = len(filtered)
    avg_distractions = sum(s.distraction_count for s in filtered) / total_sessions
    avg_score = sum(s.focus_score for s in filtered) / total_sessions

    print(f"\n📊 Focus summary ({args.days}d)")
    print(f"Sessions: {total_sessions}")
    print(f"Total minutes: {total_minutes}")
    print(f"Avg distractions/session: {avg_distractions:.2f}")
    print(f"Avg focus score: {avg_score:.1f}")
    print(f"\n💡 AI-style suggestion: {_suggestion(avg_distractions, avg_score)}")
    return 0


def cmd_today(_: argparse.Namespace) -> int:
    sessions = _load_sessions()
    today_ord = date.today().toordinal()
    today_sessions = []

    for s in sessions:
        try:
            if datetime.fromisoformat(s.started_at.replace("Z", "")).date().toordinal() == today_ord:
                today_sessions.append(s)
        except ValueError:
            continue

    if not today_sessions:
        print("No sessions logged today yet.")
        return 0

    minutes = sum(s.minutes for s in today_sessions)
    avg_score = sum(s.focus_score for s in today_sessions) / len(today_sessions)
    print(f"Today: {len(today_sessions)} sessions, {minutes} minutes, avg focus score {avg_score:.1f}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="remote-focus",
        description="Remote Work Focus Tracker - track and score focus sessions.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_log = sub.add_parser("log", help="Log a new focus session")
    p_log.add_argument("--minutes", type=int, required=True)
    p_log.add_argument("--distractions", type=int, default=0)
    p_log.add_argument("--notes", type=str, default="")
    p_log.set_defaults(func=cmd_log)

    p_summary = sub.add_parser("summary", help="Show focus summary")
    p_summary.add_argument("--days", type=int, default=7)
    p_summary.set_defaults(func=cmd_summary)

    p_today = sub.add_parser("today", help="Show today's focus snapshot")
    p_today.set_defaults(func=cmd_today)

    return parser


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if getattr(args, "minutes", 5) < 5:
        print("Error: --minutes must be >= 5")
        return 2
    if getattr(args, "days", 1) < 1:
        print("Error: --days must be >= 1")
        return 2
    if getattr(args, "distractions", 0) < 0:
        print("Error: --distractions must be >= 0")
        return 2

    return args.func(args)
