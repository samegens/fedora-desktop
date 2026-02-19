#!/usr/bin/env python3
"""
Analyzes Ansible log files and generates a summary of changes and diffs.
"""
import sys
import re
from pathlib import Path
from typing import TypedDict


class TaskInfo(TypedDict):
    """Information about an Ansible task."""
    task: str
    status: str | None
    diff: str | None


# Statuses to ignore in the summary (organizational tasks that don't represent actual work)
IGNORED_STATUSES = {'included'}


def strip_ansi_codes(text: str) -> str:
    """Remove ANSI color codes from text."""
    ansi_pattern = re.compile(r'\x1B\[[0-9;]*[a-zA-Z]')
    return ansi_pattern.sub('', text)


def clean_diff_lines(diff_lines: list[str]) -> list[str]:
    """Remove lines between diff sections using @@ headers to identify content."""
    if not diff_lines:
        return []

    cleaned: list[str] = []
    i = 0
    while i < len(diff_lines):
        line = diff_lines[i]
        clean_line = strip_ansi_codes(line).strip()

        # Check if this is a @@ header
        hunk_match = re.match(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', clean_line)
        if hunk_match:
            # Add the header line
            cleaned.append(line)
            i += 1

            # Parse the number of lines in this hunk
            old_count = int(hunk_match.group(2)) if hunk_match.group(2) else 1
            new_count = int(hunk_match.group(4)) if hunk_match.group(4) else 1

            # Read hunk content by counting actual old/new lines
            old_read = 0
            new_read = 0
            while i < len(diff_lines) and (old_read < old_count or new_read < new_count):
                next_line = diff_lines[i]
                next_clean = strip_ansi_codes(next_line).strip()

                # Stop if we hit another section header
                if next_clean.startswith('---') or next_clean.startswith('@'):
                    break

                # Skip '\ No newline at end of file' markers (not counted in hunk)
                if next_clean.startswith('\\'):
                    cleaned.append(next_line)
                    i += 1
                    continue

                # Count this line
                if next_clean.startswith('+'):
                    new_read += 1
                elif next_clean.startswith('-'):
                    old_read += 1
                else:
                    # Context line counts for both
                    old_read += 1
                    new_read += 1

                cleaned.append(next_line)
                i += 1

            # Skip any blank lines after the hunk until next section
            while i < len(diff_lines):
                next_clean = strip_ansi_codes(diff_lines[i]).strip()
                if not next_clean:
                    i += 1  # Skip blank line
                else:
                    break  # Hit non-blank, stop skipping
        else:
            # Not a hunk header, just add header lines (---, +++)
            if clean_line.startswith('---') or clean_line.startswith('+++'):
                cleaned.append(line)
            # Skip blank lines between sections
            i += 1

    return cleaned


def parse_ansible_log(log_content: str) -> list[TaskInfo]:
    """Parse Ansible log content and extract task changes and diffs.

    Args:
        log_content: The log content as a string

    Returns:
        List of TaskInfo dictionaries
    """
    lines = log_content.splitlines(keepends=True)

    tasks: list[TaskInfo] = []
    current_task: str | None = None
    current_status: str | None = None
    diff_lines: list[str] = []
    in_diff = False

    for line in lines:
        # Check if line has timestamp prefix
        # Ansible 2.17: "2025-10-05 07:34:20,993 p=1846425 u=sebastiaan n=ansible | "
        # Ansible 2.18+: "2025-10-05 07:34:20,993 p=1846425 u=sebastiaan n=ansible INFO| "
        timestamp_pattern = r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+ p=\d+ u=\S+ n=\S+) (?:INFO|DEBUG|WARNING|ERROR|CRITICAL)?\| (.*)$'
        timestamp_match = re.match(timestamp_pattern, line)
        has_timestamp = timestamp_match is not None

        if has_timestamp and timestamp_match:
            line = timestamp_match.group(2)

        # Detect task headers
        task_match = re.search(r'TASK \[(.*?)\]', line)
        if task_match:
            # Save previous task if exists
            if current_task:
                cleaned_lines = clean_diff_lines(diff_lines)
                tasks.append({
                    'task': current_task,
                    'status': current_status,
                    'diff': '\n'.join(cleaned_lines) if cleaned_lines else None
                })

            current_task = task_match.group(1)
            current_status = None
            diff_lines = []
            in_diff = False
            continue

        # Detect diff start (appears before or after status line, including in loops)
        if current_task:
            # Look for diff markers
            if re.search(r'^(\x1B\[[\d;]*m)*---', line) or line.startswith('--- before:') or line.startswith('--- '):
                in_diff = True
                diff_lines.append(line.rstrip())
                continue
            elif in_diff:
                # In diff mode, capture everything until we hit a line with timestamp that's not part of diff
                # or until we see the status line
                if has_timestamp and re.search(r'^(ok|skipping|changed|failed|fatal|included):', line):
                    # This is the status line, end of diff
                    status_match = re.match(r'^(ok|skipping|changed|failed|fatal|included):', line)
                    if status_match:
                        new_status = status_match.group(1)
                        # Treat fatal as failed
                        if new_status == 'fatal':
                            new_status = 'failed'
                        # Priority: failed > changed > ok > skipping > included
                        status_priority: dict[str | None, int] = {'failed': 5, 'changed': 4, 'ok': 3, 'skipping': 2, 'included': 1, None: 0}
                        if status_priority[new_status] > status_priority[current_status]:
                            current_status = new_status
                        in_diff = False
                    continue
                elif not has_timestamp or not line.strip():
                    # Lines without timestamp are continuation of diff, or empty lines
                    diff_lines.append(line.rstrip())
                    continue
                else:
                    # New timestamped line that's not a status - end diff
                    in_diff = False

        # Detect status (only on timestamped lines)
        if current_task and has_timestamp:
            if re.search(r'^(ok|skipping|changed|failed|fatal|included):', line):
                status_match = re.match(r'^(ok|skipping|changed|failed|fatal|included):', line)
                if status_match:
                    new_status = status_match.group(1)
                    # Treat fatal as failed
                    if new_status == 'fatal':
                        new_status = 'failed'
                    # Priority: failed > changed > ok > skipping > included
                    status_priority: dict[str | None, int] = {'failed': 5, 'changed': 4, 'ok': 3, 'skipping': 2, 'included': 1, None: 0}
                    if status_priority[new_status] > status_priority[current_status]:
                        current_status = new_status
                    in_diff = False
                continue

    # Save final task
    if current_task:
        cleaned_lines = clean_diff_lines(diff_lines)
        tasks.append({
            'task': current_task,
            'status': current_status,
            'diff': '\n'.join(cleaned_lines) if cleaned_lines else None
        })

    # Filter out tasks with ignored statuses
    return [t for t in tasks if t['status'] not in IGNORED_STATUSES]


def generate_summary(log_path: str) -> None:
    """Generate a summary of the Ansible run from a log file."""
    with open(log_path, 'r', encoding='utf-8') as f:
        log_content = f.read()

    tasks = parse_ansible_log(log_content)

    print("=" * 80)
    print(f"ANSIBLE RUN SUMMARY")
    print(f"Log file: {log_path}")
    print("=" * 80)
    print()

    failed_tasks = [t for t in tasks if t['status'] == 'failed']
    changed_tasks = [t for t in tasks if t['status'] == 'changed']
    ok_tasks = [t for t in tasks if t['status'] == 'ok']
    skipped_tasks = [t for t in tasks if t['status'] == 'skipping']
    unknown_tasks = [t for t in tasks if not t['status']]

    print(f"Total tasks: {len(tasks)}")
    print(f"  Changed: {len(changed_tasks)}")
    print(f"  OK: {len(ok_tasks)}")
    print(f"  Skipped: {len(skipped_tasks)}")
    if failed_tasks:
        print(f"  FAILED: {len(failed_tasks)}")
    if unknown_tasks:
        print(f"  Unknown status: {len(unknown_tasks)}")
    print()

    if changed_tasks:
        print("CHANGED TASKS:")
        print("-" * 80)
        for i, task in enumerate(changed_tasks, 1):
            print(f"{i}. {task['task']}")
            if task['diff']:
                print("   Diff:")
                for line in task['diff'].split('\n'):
                    print(f"   {line}")
            print()

    if failed_tasks:
        print("FAILED TASKS:")
        print("-" * 80)
        for i, task in enumerate(failed_tasks, 1):
            print(f"{i}. {task['task']}")
            if task['diff']:
                print("   Diff:")
                for line in task['diff'].split('\n'):
                    print(f"   {line}")
            print()

    print("=" * 80)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: summarize_log.py <log_file>")
        sys.exit(1)

    log_path = sys.argv[1]
    if not Path(log_path).exists():
        print(f"Error: Log file '{log_path}' not found")
        sys.exit(1)

    generate_summary(log_path)
