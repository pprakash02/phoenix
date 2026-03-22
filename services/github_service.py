# services/github_service.py
"""GitHub integration: repo cloning, file analysis, and PR creation."""

import os
import re
import ast
import shutil
import tempfile
from git import Repo
from github import Github, GithubException


def parse_repo_url(url: str) -> dict:
    """Parse a GitHub URL into owner and repo name."""
    url = url.strip().rstrip("/").replace(".git", "")
    match = re.match(r"https?://github\.com/([^/]+)/([^/]+)", url)
    if not match:
        raise ValueError(f"Invalid GitHub URL: {url}")
    return {"owner": match.group(1), "repo": match.group(2), "full_name": f"{match.group(1)}/{match.group(2)}"}


def clone_repo(url: str, target_dir: str = None) -> str:
    """
    Clone a GitHub repository to a local directory.
    Returns the absolute path to the cloned repo.
    """
    if target_dir is None:
        target_dir = tempfile.mkdtemp(prefix="phoenix_repo_")

    if os.path.exists(target_dir) and os.listdir(target_dir):
        shutil.rmtree(target_dir)

    print(f"[GITHUB] Cloning {url} → {target_dir}")
    Repo.clone_from(url, target_dir, depth=1)
    print(f"[GITHUB] Clone complete: {target_dir}")
    return target_dir


def analyze_repo_files(repo_dir: str) -> list[dict]:
    """
    Discover all Python files in the repo and extract metadata.
    Returns a list of dicts with path, name, function count, and size.
    """
    files = []
    for root, dirs, filenames in os.walk(repo_dir):
        # Skip hidden dirs, __pycache__, .git, venv, node_modules
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in
                   ("__pycache__", "venv", ".venv", "node_modules", "env")]

        for fname in filenames:
            if not fname.endswith(".py") or fname == "__init__.py":
                continue

            fpath = os.path.join(root, fname)
            rel_path = os.path.relpath(fpath, repo_dir)
            size = os.path.getsize(fpath)

            # Extract function info
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    source = f.read()
                tree = ast.parse(source)
                functions = []
                for node in ast.iter_child_nodes(tree):
                    if isinstance(node, ast.FunctionDef):
                        args = [a.arg for a in node.args.args]
                        uses_input = any(
                            isinstance(n, ast.Call)
                            and isinstance(getattr(n, "func", None), ast.Name)
                            and n.func.id == "input"
                            for n in ast.walk(node)
                        )
                        functions.append({
                            "name": node.name,
                            "args": args,
                            "testable": not uses_input,
                        })
            except (SyntaxError, UnicodeDecodeError):
                functions = []

            testable_count = sum(1 for fn in functions if fn.get("testable"))

            files.append({
                "path": rel_path,
                "name": fname,
                "size": size,
                "functions": functions,
                "function_count": len(functions),
                "testable_count": testable_count,
                "needs_context": len(functions) > 0,
            })

    return sorted(files, key=lambda f: f["path"])


def create_pull_request(
    repo_url: str,
    token: str,
    branch_name: str,
    title: str,
    body: str,
    files: dict[str, str],
    base_branch: str = "main",
) -> dict:
    """
    Create a PR on GitHub with generated test files.
    files: dict mapping file paths (in repo) to file content.
    Returns PR URL and number.
    """
    parsed = parse_repo_url(repo_url)
    g = Github(token)

    try:
        repo = g.get_repo(parsed["full_name"])
    except GithubException as e:
        raise ValueError(f"Cannot access repo {parsed['full_name']}: {e}")

    # Get base branch ref
    base_ref = repo.get_git_ref(f"heads/{base_branch}")
    base_sha = base_ref.object.sha

    # Create new branch
    try:
        repo.create_git_ref(f"refs/heads/{branch_name}", base_sha)
    except GithubException:
        # Branch may already exist
        pass

    # Create/update files in the new branch
    for file_path, content in files.items():
        try:
            existing = repo.get_contents(file_path, ref=branch_name)
            repo.update_file(
                file_path, f"Update {file_path}", content,
                existing.sha, branch=branch_name
            )
        except GithubException:
            repo.create_file(
                file_path, f"Add {file_path}", content,
                branch=branch_name
            )

    # Create PR
    pr = repo.create_pull(
        title=title,
        body=body,
        head=branch_name,
        base=base_branch,
    )

    return {
        "url": pr.html_url,
        "number": pr.number,
        "branch": branch_name,
    }
