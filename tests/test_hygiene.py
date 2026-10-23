"""What this plugin must never contain, held here so the plugin stays what its
README says it is: instructions only, with no code to run, no credential read
from anyone's environment and nothing that downloads and runs.

The plugin directory holds a version for a reviewer, or blocks it, for each of
these: a file that reads a credential already set in a person's environment, a
package launcher, a download-and-execute command anywhere in the repository
(prose and quotation included), a system file, a symbolic link, a submodule, a
bundled MCP server file, and a bundled image written in backticks.

The patterns below are built from pieces on purpose. A test that held the
words whole would match itself, and so would fail on its own source.

Run with `python3 -m unittest discover -s tests -v` from the repository root
(stdlib only; no environment variable is read; CI runs it in checks.yml).
"""

import os
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def j(*parts):
    return "".join(parts)


# Reading a credential from the environment, or sending one in a header.
CREDENTIAL_LITERALS = [
    j("os.", "environ"),
    j("get", "env("),
    j("process.", "env"),
    j("Authori", "zation:"),
    j("Bea", "rer "),
]
CREDENTIAL_REFERENCE = re.compile(j(r"\$\{[^}]*", "(TOKEN|SECRET|KEY|PASSWORD)", r"[^}]*\}"))

# Package launchers: a command that downloads a package and runs it.
LAUNCHERS = [j("np", "x"), j("bun", "x"), j("pnpm d", "lx"), j("yarn d", "lx"),
             j("uv", "x"), j("pipx r", "un"), j("uv r", "un")]
LAUNCHER_PATTERNS = [re.compile(r"\b" + re.escape(name) + r"\b") for name in LAUNCHERS]

# A download piped into a shell. The directory's scanner holds this wherever it
# appears, so it is looked for line by line in every file but the one workflow
# whose comments describe it (the same exclusion the workflow's own check makes).
DOWNLOAD_AND_EXECUTE = re.compile(
    j("(cur", "l|wge", "t)[^|;]*", r"\|", r"[ \t]*(sudo[ \t]+)?(ba)?", "sh"))
DOWNLOAD_CHECK_EXCLUDES = {".github/workflows/checks.yml"}

NOT_PLUGIN_FILES = {
    ".DS_Store", "Thumbs.db", "desktop.ini", ".gitmodules", ".gitattributes",
    "CLAUDE.md", "package.json", "package-lock.json", "npm-shrinkwrap.json",
    "bun.lock", "bun.lockb", "yarn.lock", "pnpm-lock.yaml",
}
NOT_PLUGIN_SUFFIXES = (".mcpb", ".dxt")
# This plugin is instructions only: no hooks, no scripts, no bundled agents or
# evaluations, no executable folder.
NOT_PLUGIN_FOLDERS = {"__MACOSX", "bin", "hooks", "agents", "evals", "scripts"}
CODE_SUFFIXES = {".sh", ".bash", ".zsh", ".js", ".mjs", ".cjs", ".ts", ".py", ".rb",
                 ".ps1", ".bat", ".cmd"}
BINARY_SUFFIXES = {".png"}

PRICE_FIGURE = re.compile(j(r"\$", r"\d"))
PER_MONTH = re.compile(j("/m", r"o\b"))
THE_WORD = re.compile(j("offi", "cial"), re.I)
# A platform's name straight after the word "by", which reads as a claim that
# the platform made this. The maker line says "not by" it, and the trademark
# line says "Not affiliated with or endorsed by" it: both are allowed.
BY_THE_PLATFORM = re.compile(
    r"(?<!not )(?<!endorsed )\bby (Google|Meta|LinkedIn|X|TikTok|Microsoft)\b")
IMAGE_IN_BACKTICKS = re.compile(
    "`[^`\n]*\\." + j("(png|jp", "e?g|gif|webp|svg|ico|woff2?|ttf|otf)") + "\\b[^`\n]*`", re.I)


def repo_files():
    """Every file in the repository: tracked ones, plus untracked ones that are
    not ignored. Relative names, with forward slashes."""
    try:
        out = subprocess.run(
            ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
            cwd=ROOT, capture_output=True, check=True).stdout
        names = [n for n in out.decode("utf-8").split("\0") if n]
    except (OSError, subprocess.CalledProcessError):
        names = []
        for dirpath, dirs, files in os.walk(ROOT):
            dirs[:] = [d for d in dirs if d not in {".git", "__pycache__"}]
            for f in files:
                if not f.endswith(".pyc"):
                    names.append(os.path.relpath(os.path.join(dirpath, f), ROOT))
    return sorted(set(n.replace(os.sep, "/") for n in names if (ROOT / n).exists() or (ROOT / n).is_symlink()))


def text_files():
    for name in repo_files():
        path = ROOT / name
        if path.is_symlink() or not path.is_file():
            continue
        if path.suffix.lower() in BINARY_SUFFIXES:
            continue
        yield name, path.read_text(encoding="utf-8")


class Hygiene(unittest.TestCase):

    def test_the_repository_is_not_empty(self):
        self.assertGreater(len(repo_files()), 10)

    def test_nothing_reads_a_credential(self):
        for name, text in text_files():
            for literal in CREDENTIAL_LITERALS:
                self.assertNotIn(literal, text, "%s reads or sends a credential" % name)
            self.assertIsNone(CREDENTIAL_REFERENCE.search(text), name)

    def test_no_package_launcher(self):
        for name, text in text_files():
            for pattern in LAUNCHER_PATTERNS:
                self.assertIsNone(pattern.search(text), "%s: %s" % (name, pattern.pattern))

    def test_no_download_and_execute_pattern(self):
        for name, text in text_files():
            if name in DOWNLOAD_CHECK_EXCLUDES:
                continue
            for number, line in enumerate(text.split("\n"), 1):
                self.assertIsNone(DOWNLOAD_AND_EXECUTE.search(line),
                                  "%s:%d holds a download piped into a shell" % (name, number))

    def test_no_system_file_link_submodule_bundle_or_folder_that_is_not_the_plugins(self):
        for name in repo_files():
            path = ROOT / name
            parts = name.split("/")
            self.assertFalse(path.is_symlink(), "%s is a symbolic link" % name)
            self.assertNotIn(parts[-1], NOT_PLUGIN_FILES, name)
            self.assertFalse(name.endswith(NOT_PLUGIN_SUFFIXES), name)
            self.assertEqual(NOT_PLUGIN_FOLDERS & set(parts[:-1]), set(), name)

    def test_the_plugin_is_instructions_only(self):
        for name in repo_files():
            if name.startswith("tests/"):
                continue  # the tests run on a developer's machine; the plugin never runs them
            self.assertNotIn(Path(name).suffix.lower(), CODE_SUFFIXES,
                             "%s is code, and this plugin runs none" % name)

    def test_no_price_figure_anywhere(self):
        for name, text in text_files():
            self.assertIsNone(PRICE_FIGURE.search(text), "%s holds a price figure" % name)
            self.assertIsNone(PER_MONTH.search(text), "%s holds a per-month price" % name)

    def test_nothing_claims_to_be_made_by_the_platform(self):
        for name, text in text_files():
            self.assertIsNone(THE_WORD.search(text), "%s uses the word that claims standing" % name)
            match = BY_THE_PLATFORM.search(text)
            self.assertIsNone(match, "%s: %s" % (name, match.group(0) if match else ""))

    def test_no_bundled_image_is_written_in_backticks(self):
        for name, text in text_files():
            match = IMAGE_IN_BACKTICKS.search(text)
            self.assertIsNone(match, "%s: %s" % (name, match.group(0) if match else ""))

    def test_every_address_is_https(self):
        for name, text in text_files():
            self.assertNotIn("http" + "://", text, name)

    def test_the_ignore_file_keeps_local_state_out(self):
        text = (ROOT / ".gitignore").read_text(encoding="utf-8")
        for line in (".DS_Store", "Thumbs.db", ".claude/settings.local.json",
                     "__pycache__/", "*.pyc"):
            self.assertIn(line, text)


if __name__ == "__main__":
    unittest.main()
