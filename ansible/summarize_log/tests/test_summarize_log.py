#!/usr/bin/env python3
"""Unit tests for summarize_log.py"""
import re
import unittest
from summarize_log import parse_ansible_log


def has_trailing_blank_lines(text: str) -> bool:
    """Check if text ends with blank lines (containing only whitespace/ANSI codes)."""
    lines = text.split('\n')
    if len(lines) < 2:
        return False
    # Strip ANSI codes and check if last line is empty
    ansi_pattern = re.compile(r'\x1B\[[0-9;]*[a-zA-Z]')
    last_line = ansi_pattern.sub('', lines[-1])
    return not last_line.strip()


def has_blank_lines(text: str) -> bool:
    """Check if text has any blank lines (containing only whitespace/ANSI codes)."""
    ansi_pattern = re.compile(r'\x1B\[[0-9;]*[a-zA-Z]')
    lines = [ansi_pattern.sub('', line).strip() for line in text.split('\n')]
    return any(not line for line in lines)


class TestAnsibleLogParsing(unittest.TestCase):
    """Test cases for parsing Ansible logs."""

    def test_simple_changed_task_with_diff(self):
        """Test parsing a simple changed task with a diff."""
        # Arrange
        log_content = """2025-11-11 09:33:13,335 p=680107 u=sebastiaan n=ansible | TASK [Add Cargo bin to PATH] ********************************************************************************************************************************************************************
2025-11-11 09:33:13,496 p=680107 u=sebastiaan n=ansible | \x1b[0;31m--- before: /home/sebastiaan/.bashrc (content)\x1b[0m
\x1b[0;31m\x1b[0m\x1b[0;32m+++ after: /home/sebastiaan/.bashrc (content)\x1b[0m
\x1b[0;32m\x1b[0m\x1b[0;36m@@ -130,3 +130,4 @@\x1b[0m
\x1b[0;36m\x1b[0m alias pandoc='docker run --rm -v "$(pwd):/data" -u $(id -u):$(id -g) pandoc/latex'
 export HCP_ORGANIZATION_ID=ef421799-ccdd-475b-a102-8883a23b75d9
 export HCP_PROJECT_ID=23aba1d0-48a6-4891-aef7-8cf4fb1ce859
\x1b[0;32m+export PATH="$HOME/.cargo/bin:$PATH"\x1b[0m
\x1b[0;32m\x1b[0m

2025-11-11 09:33:13,497 p=680107 u=sebastiaan n=ansible | changed: [localhost] => {
    "backup": "",
    "changed": true
}

MSG:

line added

2025-11-11 09:33:13,504 p=680107 u=sebastiaan n=ansible | TASK [Next task] ****
"""

        # Act
        tasks = parse_ansible_log(log_content)

        # Assert
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0]['task'], 'Add Cargo bin to PATH')
        self.assertEqual(tasks[0]['status'], 'changed')
        self.assertIsNotNone(tasks[0]['diff'])
        self.assertIn('export PATH="$HOME/.cargo/bin:$PATH"', tasks[0]['diff'])  # type: ignore[arg-type]
        self.assertFalse(has_blank_lines(tasks[0]['diff']), "Diff should not have any blank lines")  # type: ignore[arg-type]

    def test_ok_task_no_diff(self):
        """Test parsing an 'ok' task with no diff."""
        # Arrange
        log_content = """2025-11-11 09:33:11,038 p=680107 u=sebastiaan n=ansible | TASK [Update apt cache] *************************************************************************************************************************************************************************
2025-11-11 09:33:11,848 p=680107 u=sebastiaan n=ansible | changed: [localhost] => {
    "cache_update_time": 1762842863,
    "cache_updated": true,
    "changed": true
}
2025-11-11 09:33:11,857 p=680107 u=sebastiaan n=ansible | TASK [Check if venv Python exists] **************************************************************************************************************************************************************
2025-11-11 09:33:12,076 p=680107 u=sebastiaan n=ansible | ok: [localhost] => {
    "changed": false,
    "stat": {
        "exists": true
    }
}
2025-11-11 09:33:12,087 p=680107 u=sebastiaan n=ansible | TASK [Next task] ****
"""

        # Act
        tasks = parse_ansible_log(log_content)

        # Assert
        self.assertEqual(len(tasks), 3)
        self.assertEqual(tasks[0]['task'], 'Update apt cache')
        self.assertEqual(tasks[0]['status'], 'changed')
        self.assertIsNone(tasks[0]['diff'])

        self.assertEqual(tasks[1]['task'], 'Check if venv Python exists')
        self.assertEqual(tasks[1]['status'], 'ok')
        self.assertIsNone(tasks[1]['diff'])

    def test_status_priority(self):
        """Test that status priority is respected (changed > ok > skipping)."""
        # Arrange
        log_content = """2025-11-11 09:33:13,504 p=680107 u=sebastiaan n=ansible | TASK [Multiple status task] ****
2025-11-11 09:33:13,672 p=680107 u=sebastiaan n=ansible | ok: [localhost] => {
    "changed": false
}
2025-11-11 09:33:13,820 p=680107 u=sebastiaan n=ansible | changed: [localhost] => {
    "changed": true
}
2025-11-11 09:33:13,975 p=680107 u=sebastiaan n=ansible | TASK [Next task] ****
"""

        # Act
        tasks = parse_ansible_log(log_content)

        # Assert
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0]['task'], 'Multiple status task')
        self.assertEqual(tasks[0]['status'], 'changed')

    def test_skipping_task(self):
        """Test parsing a skipped task."""
        # Arrange
        log_content = """2025-11-11 09:33:11,038 p=680107 u=sebastiaan n=ansible | TASK [Conditional task] *************************************************************************************************************************************************************************
2025-11-11 09:33:11,848 p=680107 u=sebastiaan n=ansible | skipping: [localhost] => {
    "changed": false,
    "skip_reason": "Conditional result was False"
}
2025-11-11 09:33:11,857 p=680107 u=sebastiaan n=ansible | TASK [Next task] ****
"""

        # Act
        tasks = parse_ansible_log(log_content)

        # Assert
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0]['task'], 'Conditional task')
        self.assertEqual(tasks[0]['status'], 'skipping')
        self.assertIsNone(tasks[0]['diff'])

    def test_multiple_tasks(self):
        """Test parsing multiple tasks in sequence."""
        # Arrange
        log_content = """2025-11-11 09:33:11,038 p=680107 u=sebastiaan n=ansible | TASK [First task] ****
2025-11-11 09:33:11,848 p=680107 u=sebastiaan n=ansible | ok: [localhost]
2025-11-11 09:33:11,857 p=680107 u=sebastiaan n=ansible | TASK [Second task] ****
2025-11-11 09:33:12,076 p=680107 u=sebastiaan n=ansible | changed: [localhost]
2025-11-11 09:33:12,087 p=680107 u=sebastiaan n=ansible | TASK [Third task] ****
2025-11-11 09:33:12,100 p=680107 u=sebastiaan n=ansible | skipping: [localhost]
"""

        # Act
        tasks = parse_ansible_log(log_content)

        # Assert
        self.assertEqual(len(tasks), 3)
        self.assertEqual(tasks[0]['task'], 'First task')
        self.assertEqual(tasks[0]['status'], 'ok')
        self.assertEqual(tasks[1]['task'], 'Second task')
        self.assertEqual(tasks[1]['status'], 'changed')
        self.assertEqual(tasks[2]['task'], 'Third task')
        self.assertEqual(tasks[2]['status'], 'skipping')

    def test_ansible_2_18_log_format_with_info_level(self):
        """Test parsing Ansible 2.18+ log format with INFO| separator."""
        # Arrange
        log_content = """2025-11-11 12:08:11,871 p=923925 u=sebastiaan n=ansible INFO| PLAY [Configure Ubuntu desktop] *****************************************************************************************************************************************************************
2025-11-11 12:08:11,886 p=923925 u=sebastiaan n=ansible INFO| TASK [Gathering Facts] **************************************************************************************************************************************************************************
2025-11-11 12:08:13,251 p=923925 u=sebastiaan n=ansible INFO| ok: [localhost]
2025-11-11 12:08:13,259 p=923925 u=sebastiaan n=ansible INFO| TASK [Update apt cache] *************************************************************************************************************************************************************************
2025-11-11 12:08:13,967 p=923925 u=sebastiaan n=ansible INFO| ok: [localhost] => {
    "cache_update_time": 1762857166,
    "cache_updated": false,
    "changed": false
}
2025-11-11 12:08:14,894 p=923925 u=sebastiaan n=ansible INFO| TASK [Add git branch to bash prompt] ************************************************************************************************************************************************************
2025-11-11 12:08:15,124 p=923925 u=sebastiaan n=ansible INFO| ok: [localhost] => {
    "changed": false
}
2025-11-11 12:08:15,706 p=923925 u=sebastiaan n=ansible INFO| TASK [Add aliases] ******************************************************************************************************************************************************************************
2025-11-11 12:08:16,142 p=923925 u=sebastiaan n=ansible INFO| \x1b[0;31m--- before: /home/sebastiaan/.bashrc (content)\x1b[0m
\x1b[0;31m\x1b[0m\x1b[0;32m+++ after: /home/sebastiaan/.bashrc (content)\x1b[0m
\x1b[0;32m\x1b[0m\x1b[0;36m@@ -133,3 +133,4 @@\x1b[0m
\x1b[0;36m\x1b[0m export PATH="$HOME/.cargo/bin:$PATH"
 alias sizeof='du -sh'
 alias ds='docker run --rm -it -v "$(pwd):/data" $1 /bin/bash'
\x1b[0;32m+ds() { docker run --rm -it -v "$(pwd):/data" "$1" /bin/bash; }\x1b[0m
\x1b[0;32m\x1b[0m

2025-11-11 12:08:16,143 p=923925 u=sebastiaan n=ansible INFO| changed: [localhost] => (item=ds() { docker run --rm -it -v "$(pwd):/data" "$1" /bin/bash; }) => {
    "ansible_loop_var": "item",
    "backup": "",
    "changed": true,
    "item": "ds() { docker run --rm -it -v \\"$(pwd):/data\\" \\"$1\\" /bin/bash; }"
}

MSG:

line added

2025-11-11 12:08:16,144 p=923925 u=sebastiaan n=ansible INFO| PLAY RECAP **************************************************************************************************************************************************************************************
"""

        # Act
        tasks = parse_ansible_log(log_content)

        # Assert
        self.assertEqual(len(tasks), 4)
        self.assertEqual(tasks[0]['task'], 'Gathering Facts')
        self.assertEqual(tasks[0]['status'], 'ok')

        self.assertEqual(tasks[1]['task'], 'Update apt cache')
        self.assertEqual(tasks[1]['status'], 'ok')

        self.assertEqual(tasks[2]['task'], 'Add git branch to bash prompt')
        self.assertEqual(tasks[2]['status'], 'ok')

        self.assertEqual(tasks[3]['task'], 'Add aliases')
        self.assertEqual(tasks[3]['status'], 'changed')
        self.assertIsNotNone(tasks[3]['diff'])
        self.assertIn('ds() { docker run --rm -it -v "$(pwd):/data" "$1" /bin/bash; }', tasks[3]['diff'])  # type: ignore[arg-type]

    def test_loop_task_with_diffs(self):
        """Test that diffs from loop items are captured."""
        # Arrange
        log_content = """2025-11-11 09:33:13,504 p=680107 u=sebastiaan n=ansible | TASK [Add aliases] ******************************************************************************************************************************************************************************
2025-11-11 09:33:13,672 p=680107 u=sebastiaan n=ansible | ok: [localhost] => (item=alias pandoc='docker run --rm -v "$(pwd):/data" -u $(id -u):$(id -g) pandoc/latex') => {
    "ansible_loop_var": "item",
    "backup": "",
    "changed": false,
    "item": "alias pandoc='docker run --rm -v \"$(pwd):/data\" -u $(id -u):$(id -g) pandoc/latex'"
}
2025-11-11 09:33:13,819 p=680107 u=sebastiaan n=ansible | \x1b[0;31m--- before: /home/sebastiaan/.bashrc (content)\x1b[0m
\x1b[0;31m\x1b[0m\x1b[0;32m+++ after: /home/sebastiaan/.bashrc (content)\x1b[0m
\x1b[0;32m\x1b[0m\x1b[0;36m@@ -130,3 +130,4 @@\x1b[0m
\x1b[0;36m\x1b[0m alias pandoc='docker run --rm -v "$(pwd):/data" -u $(id -u):$(id -g) pandoc/latex'
 export HCP_ORGANIZATION_ID=ef421799-ccdd-475b-a102-8883a23b75d9
 export HCP_PROJECT_ID=23aba1d0-48a6-4891-aef7-8cf4fb1ce859
\x1b[0;32m+alias sizeof='du -sh'\x1b[0m
\x1b[0;32m\x1b[0m

2025-11-11 09:33:13,820 p=680107 u=sebastiaan n=ansible | changed: [localhost] => (item=alias sizeof='du -sh') => {
    "ansible_loop_var": "item",
    "backup": "",
    "changed": true,
    "item": "alias sizeof='du -sh'"
}

MSG:

line added

2025-11-11 09:33:13,973 p=680107 u=sebastiaan n=ansible | \x1b[0;31m--- before: /home/sebastiaan/.bashrc (content)\x1b[0m
\x1b[0;31m\x1b[0m\x1b[0;32m+++ after: /home/sebastiaan/.bashrc (content)\x1b[0m
\x1b[0;32m\x1b[0m\x1b[0;36m@@ -130,3 +130,4 @@\x1b[0m
\x1b[0;36m\x1b[0m alias pandoc='docker run --rm -v "$(pwd):/data" -u $(id -u):$(id -g) pandoc/latex'
 export HCP_ORGANIZATION_ID=ef421799-ccdd-475b-a102-8883a23b75d9
 export HCP_PROJECT_ID=23aba1d0-48a6-4891-aef7-8cf4fb1ce859
\x1b[0;32m+alias ds='docker run --rm -it -v "$(pwd):/data" $1 /bin/bash'\x1b[0m
\x1b[0;32m\x1b[0m

2025-11-11 09:33:13,973 p=680107 u=sebastiaan n=ansible | changed: [localhost] => (item=alias ds='docker run --rm -it -v "$(pwd):/data" $1 /bin/bash') => {
    "ansible_loop_var": "item",
    "backup": "",
    "changed": true,
    "item": "alias ds='docker run --rm -it -v \"$(pwd):/data\" $1 /bin/bash'"
}

MSG:

line added

2025-11-11 09:33:13,975 p=680107 u=sebastiaan n=ansible | PLAY RECAP **************************************************************************************************************************************************************************************
"""

        # Act
        tasks = parse_ansible_log(log_content)

        # Assert
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]['task'], 'Add aliases')
        self.assertEqual(tasks[0]['status'], 'changed')
        self.assertIsNotNone(tasks[0]['diff'])
        self.assertIn('alias sizeof', tasks[0]['diff'])  # type: ignore[arg-type]
        self.assertIn('alias ds', tasks[0]['diff'])  # type: ignore[arg-type]
        self.assertFalse(has_blank_lines(tasks[0]['diff']), "Diff should not have any blank lines")  # type: ignore[arg-type]

    def test_failed_task(self):
        """Test parsing a failed task."""
        # Arrange
        log_content = """2025-11-11 09:33:11,038 p=680107 u=sebastiaan n=ansible | TASK [Install package] **************************************************************************************************************************************************************************
2025-11-11 09:33:11,848 p=680107 u=sebastiaan n=ansible | failed: [localhost] => {
    "changed": false,
    "msg": "Package not found"
}
2025-11-11 09:33:11,857 p=680107 u=sebastiaan n=ansible | TASK [Next task] ****
"""

        # Act
        tasks = parse_ansible_log(log_content)

        # Assert
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0]['task'], 'Install package')
        self.assertEqual(tasks[0]['status'], 'failed')
        self.assertIsNone(tasks[0]['diff'])

    def test_status_priority_with_failed(self):
        """Test that status priority includes failed (failed > changed > ok > skipping)."""
        # Arrange
        log_content = """2025-11-11 09:33:13,504 p=680107 u=sebastiaan n=ansible | TASK [Multiple status task] ****
2025-11-11 09:33:13,672 p=680107 u=sebastiaan n=ansible | ok: [localhost] => {
    "changed": false
}
2025-11-11 09:33:13,820 p=680107 u=sebastiaan n=ansible | changed: [localhost] => {
    "changed": true
}
2025-11-11 09:33:13,950 p=680107 u=sebastiaan n=ansible | failed: [localhost] => {
    "changed": false,
    "msg": "Something went wrong"
}
2025-11-11 09:33:13,975 p=680107 u=sebastiaan n=ansible | TASK [Next task] ****
"""

        # Act
        tasks = parse_ansible_log(log_content)

        # Assert
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0]['task'], 'Multiple status task')
        self.assertEqual(tasks[0]['status'], 'failed')

    def test_fatal_error_task(self):
        """Test parsing a task with fatal error (should be treated as failed)."""
        # Arrange
        log_content = """2025-12-20 20:52:46,285 p=113862 u=sebastiaan n=ansible | TASK [Extract Double Commander] ************************************************
2025-12-20 20:52:46,721 p=113862 u=sebastiaan n=ansible | fatal: [localhost]: FAILED! => {
    "changed": false
}

MSG:

Source '/tmp/doublecmd-1.1.30.tar.xz' does not exist

2025-12-20 20:52:46,722 p=113862 u=sebastiaan n=ansible | PLAY RECAP *********************************************************************
"""

        # Act
        tasks = parse_ansible_log(log_content)

        # Assert
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]['task'], 'Extract Double Commander')
        self.assertEqual(tasks[0]['status'], 'failed')
        self.assertIsNone(tasks[0]['diff'])

    def test_included_task_ignored(self):
        """Test that include_tasks are ignored and not included in results."""
        # Arrange
        log_content = """2026-01-02 14:57:46,088 p=983539 u=sebastiaan n=ansible INFO| TASK [Install P4Merge] *************************************************************************************************************************************************************************
2026-01-02 14:57:46,090 p=983539 u=sebastiaan n=ansible INFO| included: /home/sebastiaan/Dropbox/git/ubuntu-desktop/ansible/tasks/p4merge.yml for localhost
2026-01-02 14:57:46,093 p=983539 u=sebastiaan n=ansible INFO| TASK [Next task] ****
2026-01-02 14:57:46,100 p=983539 u=sebastiaan n=ansible INFO| ok: [localhost]
"""

        # Act
        tasks = parse_ansible_log(log_content)

        # Assert
        # Should only see "Next task", not "Install P4Merge"
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]['task'], 'Next task')
        self.assertEqual(tasks[0]['status'], 'ok')


    def test_diff_with_no_newline_at_end_of_file(self):
        r"""Test that '\ No newline at end of file' doesn't truncate diff output."""
        # Arrange
        log_content = """2026-02-11 18:07:27,335 p=680107 u=sebastiaan n=ansible | TASK [Configure borgmatic] ****
2026-02-11 18:07:27,496 p=680107 u=sebastiaan n=ansible | --- before: /etc/borgmatic/config.yaml
+++ after: /tmp/config.yaml.j2
@@ -1,2 +1,4 @@
 keep_daily: 7
-keep_monthly: 6
\\ No newline at end of file
+keep_monthly: 6
+
+frequency: 1 week
\\ No newline at end of file

2026-02-11 18:07:27,497 p=680107 u=sebastiaan n=ansible | changed: [cubi] => {
    "changed": true
}
2026-02-11 18:07:27,504 p=680107 u=sebastiaan n=ansible | TASK [Next task] ****
"""

        # Act
        tasks = parse_ansible_log(log_content)

        # Assert
        self.assertIn('frequency: 1 week', tasks[0]['diff'])  # type: ignore[arg-type]


if __name__ == '__main__':
    unittest.main()
