#!/usr/bin/env python3
"""
Content Loop - Meta-Learning (Level 2)

Level 1: Content improves (hooks, images, CTAs get better based on performance)
Level 2: The SYSTEM improves (skills get amended, new skills get created, workflows get fixed)

This module monitors skill execution patterns and proposes structural improvements
to the content creation system itself — not just what content to make, but HOW
the system makes content.

Three functions:
  1. observe()  — Log skill execution outcomes (success/failure/error)
  2. inspect()  — Detect degrading skills and recurring workarounds
  3. propose()  — Suggest skill amendments or new skill creation
"""

import json
import os
import sys
from datetime import datetime, timedelta
from collections import defaultdict
from typing import List, Dict, Optional, Tuple


DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
SKILL_LOG = os.path.join(DATA_DIR, "skill-executions.jsonl")
KNOWLEDGE_DIR = os.path.join(os.path.dirname(__file__), "..", "knowledge")
SKILLS_DIR = os.path.join(os.path.dirname(__file__), "..", "skills")


# ── Observe ──────────────────────────────────────────────────────

def observe(skill_name: str, task: str, success: bool,
            error: str = None, duration_ms: int = None,
            workaround: str = None, notes: str = None):
    """Log a skill execution outcome.
    
    Call this after every skill use — successful or not.
    The workaround field captures when the agent had to deviate
    from the skill's instructions to get a result.
    
    Args:
        skill_name:   Name of the skill used (e.g. "content-creator")
        task:         What was attempted (e.g. "generate slideshow for hook test")
        success:      Did the skill produce the expected output?
        error:        Error message if failed
        duration_ms:  How long the execution took
        workaround:   If the agent had to deviate, what did it do instead?
        notes:        Any additional context
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "type": "skill_execution",
        "skill": skill_name,
        "task": task,
        "success": success,
    }
    if error:
        entry["error"] = error
    if duration_ms is not None:
        entry["duration_ms"] = duration_ms
    if workaround:
        entry["workaround"] = workaround
    if notes:
        entry["notes"] = notes
    
    with open(SKILL_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")
    
    status = "✅" if success else "❌"
    print(f"{status} Logged: {skill_name} → {task[:60]}")
    return entry


# ── Inspect ──────────────────────────────────────────────────────

def _load_skill_log() -> List[dict]:
    """Load all skill execution entries."""
    if not os.path.exists(SKILL_LOG):
        return []
    entries = []
    with open(SKILL_LOG) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return [e for e in entries if e.get("type") == "skill_execution"]


def inspect(days: int = 7, failure_threshold: float = 0.3,
            consecutive_failures: int = 3) -> Dict:
    """Analyze skill execution history for degradation patterns.
    
    Flags:
      - Skills with failure rate > threshold in the lookback window
      - Skills with N+ consecutive failures
      - Recurring workarounds (same workaround used 3+ times = missing skill)
    
    Returns a report dict with flagged skills and proposed actions.
    """
    entries = _load_skill_log()
    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
    recent = [e for e in entries if e.get("timestamp", "") >= cutoff]
    
    if not recent:
        return {"status": "no_data", "message": f"No skill executions in last {days} days"}
    
    # ── Per-skill failure rates ──
    skill_stats = defaultdict(lambda: {"total": 0, "failures": 0, "errors": [], "recent": []})
    for e in recent:
        name = e.get("skill", "unknown")
        skill_stats[name]["total"] += 1
        skill_stats[name]["recent"].append(e.get("success", True))
        if not e.get("success", True):
            skill_stats[name]["failures"] += 1
            if e.get("error"):
                skill_stats[name]["errors"].append(e["error"])
    
    flagged_skills = []
    for name, stats in skill_stats.items():
        rate = stats["failures"] / stats["total"] if stats["total"] > 0 else 0
        
        # Check failure rate threshold
        if rate >= failure_threshold and stats["total"] >= 3:
            flagged_skills.append({
                "skill": name,
                "reason": "high_failure_rate",
                "failure_rate": round(rate, 2),
                "total_runs": stats["total"],
                "failures": stats["failures"],
                "common_errors": list(set(stats["errors"]))[:3],
            })
        
        # Check consecutive failures
        consec = 0
        max_consec = 0
        for s in stats["recent"]:
            if not s:
                consec += 1
                max_consec = max(max_consec, consec)
            else:
                consec = 0
        
        if max_consec >= consecutive_failures:
            # Don't double-flag
            existing = [f for f in flagged_skills if f["skill"] == name]
            if not existing:
                flagged_skills.append({
                    "skill": name,
                    "reason": "consecutive_failures",
                    "consecutive": max_consec,
                    "total_runs": stats["total"],
                })
    
    # ── Recurring workarounds (missing skill signal) ──
    workarounds = defaultdict(int)
    workaround_contexts = defaultdict(list)
    for e in recent:
        wa = e.get("workaround")
        if wa:
            workarounds[wa] += 1
            workaround_contexts[wa].append(e.get("task", ""))
    
    missing_skills = []
    for wa, count in workarounds.items():
        if count >= 3:
            missing_skills.append({
                "workaround": wa,
                "occurrences": count,
                "contexts": workaround_contexts[wa][:3],
                "suggestion": f"Create a skill for: {wa}",
            })
    
    return {
        "status": "inspected",
        "period_days": days,
        "total_executions": len(recent),
        "unique_skills": len(skill_stats),
        "flagged_skills": flagged_skills,
        "missing_skills": missing_skills,
    }


# ── Propose ──────────────────────────────────────────────────────

def propose(report: Dict) -> List[Dict]:
    """Given an inspection report, propose concrete amendments.
    
    Returns a list of proposed actions:
      - amend_skill: Change a SKILL.md's instructions
      - create_skill: A recurring workaround should become a formal skill
      - escalate: Failure pattern too complex for auto-fix
    """
    proposals = []
    
    for skill in report.get("flagged_skills", []):
        if skill["reason"] == "high_failure_rate":
            proposals.append({
                "action": "amend_skill",
                "skill": skill["skill"],
                "priority": "high" if skill["failure_rate"] > 0.5 else "medium",
                "reason": f"{skill['failure_rate']*100:.0f}% failure rate over {skill['total_runs']} runs",
                "common_errors": skill.get("common_errors", []),
                "suggestion": "Review SKILL.md for outdated instructions, "
                             "broken API endpoints, or missing error handling. "
                             "Check if the environment changed since the skill was written.",
            })
        elif skill["reason"] == "consecutive_failures":
            proposals.append({
                "action": "amend_skill",
                "skill": skill["skill"],
                "priority": "high",
                "reason": f"{skill['consecutive']} consecutive failures",
                "suggestion": "Likely a breaking change in a dependency or API. "
                             "Check recent changes to tools the skill relies on.",
            })
    
    for missing in report.get("missing_skills", []):
        proposals.append({
            "action": "create_skill",
            "workaround": missing["workaround"],
            "priority": "medium",
            "occurrences": missing["occurrences"],
            "reason": f"Same workaround used {missing['occurrences']} times — "
                     f"this should be a formal skill",
            "suggestion": f"Create a dedicated skill that handles: {missing['workaround']}. "
                         f"Used in contexts: {', '.join(missing['contexts'][:2])}",
            "contexts": missing["contexts"],
        })
    
    # If there are high-priority issues with no clear fix pattern
    high_prio_no_fix = [p for p in proposals 
                        if p["priority"] == "high" and not p.get("common_errors")]
    for p in high_prio_no_fix:
        p["action"] = "escalate"
        p["suggestion"] = "Manual investigation needed — no clear error pattern"
    
    return proposals


# ── CLI ──────────────────────────────────────────────────────────

def print_report(report: Dict, proposals: List[Dict]):
    """Pretty-print an inspection report with proposals."""
    print("\n" + "=" * 60)
    print("🔍 SKILL HEALTH REPORT")
    print("=" * 60)
    print(f"Period: last {report['period_days']} days")
    print(f"Total executions: {report['total_executions']}")
    print(f"Unique skills: {report['unique_skills']}")
    
    if report["flagged_skills"]:
        print(f"\n⚠️  FLAGGED SKILLS ({len(report['flagged_skills'])})")
        print("-" * 40)
        for s in report["flagged_skills"]:
            if s["reason"] == "high_failure_rate":
                print(f"  ❌ {s['skill']}: {s['failure_rate']*100:.0f}% failure rate "
                      f"({s['failures']}/{s['total_runs']} runs)")
                for err in s.get("common_errors", []):
                    print(f"     └─ {err[:80]}")
            elif s["reason"] == "consecutive_failures":
                print(f"  🔴 {s['skill']}: {s['consecutive']} consecutive failures")
    else:
        print("\n✅ No degrading skills detected")
    
    if report["missing_skills"]:
        print(f"\n🆕 MISSING SKILLS ({len(report['missing_skills'])})")
        print("-" * 40)
        for m in report["missing_skills"]:
            print(f"  💡 \"{m['workaround']}\" — used {m['occurrences']} times")
            print(f"     └─ Suggestion: {m['suggestion']}")
    
    if proposals:
        print(f"\n📋 PROPOSED ACTIONS ({len(proposals)})")
        print("-" * 40)
        for i, p in enumerate(proposals, 1):
            icon = {"amend_skill": "🔧", "create_skill": "🆕", "escalate": "🚨"}.get(p["action"], "❓")
            print(f"  {i}. {icon} [{p['priority'].upper()}] {p['action']}: {p.get('skill', p.get('workaround', '?'))}")
            print(f"     Reason: {p['reason']}")
            print(f"     → {p['suggestion']}")
    
    print("\n" + "=" * 60)


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python meta.py observe <skill> <task> <success|failure> [--error msg] [--workaround wa]")
        print("  python meta.py inspect [--days N]")
        print("  python meta.py report [--days N]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "observe":
        if len(sys.argv) < 5:
            print("Usage: python meta.py observe <skill> <task> <success|failure>")
            sys.exit(1)
        skill = sys.argv[2]
        task = sys.argv[3]
        success = sys.argv[4].lower() in ("success", "true", "1", "yes")
        
        error = None
        workaround = None
        for i, arg in enumerate(sys.argv[5:], 5):
            if arg == "--error" and i + 1 < len(sys.argv):
                error = sys.argv[i + 1]
            elif arg == "--workaround" and i + 1 < len(sys.argv):
                workaround = sys.argv[i + 1]
        
        observe(skill, task, success, error=error, workaround=workaround)
    
    elif cmd in ("inspect", "report"):
        days = 7
        for i, arg in enumerate(sys.argv[2:], 2):
            if arg == "--days" and i + 1 < len(sys.argv):
                days = int(sys.argv[i + 1])
        
        report = inspect(days=days)
        if report["status"] == "no_data":
            print(f"No skill execution data in last {days} days.")
            print(f"Log file: {SKILL_LOG}")
            sys.exit(0)
        
        proposals = propose(report)
        print_report(report, proposals)
    
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
