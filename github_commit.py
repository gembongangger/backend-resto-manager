#!/usr/bin/env python3
import subprocess
import sys
import os

class GitHubCommit:
    def __init__(self, remote_url=None):
        self.remote_url = remote_url
        self.repo_path = os.getcwd()
    
    def run(self, command, capture_output=True):
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=capture_output, 
            text=True
        )
        if result.returncode != 0 and capture_output:
            print(f"Error: {result.stderr}")
            return ""
        return result.stdout.strip() if capture_output else True
    
    def init(self):
        if os.path.exists(".git"):
            print("Git repo already initialized")
            return True
        return self.run("git init")
    
    def set_remote(self, url):
        remotes_output = self.run("git remote -v")
        has_origin = "origin" in remotes_output if remotes_output else False
        if has_origin:
            self.run(f"git remote set-url origin {url}")
        else:
            self.run(f"git remote add origin {url}")
        self.remote_url = url
    
    def set_identity(self, email, name):
        self.run(f'git config user.email "{email}"')
        self.run(f'git config user.name "{name}"')
    
    def add_all(self):
        return self.run("git add .")
    
    def commit(self, message):
        if not message:
            print("Commit message required")
            return False
        return self.run(f'git commit -m "{message}"')
    
    def push(self, branch="main"):
        return self.run(f"git push -u origin {branch}")
    
    def status(self):
        return self.run("git status")
    
    def log(self, n=5):
        return self.run(f"git log --oneline -{n}")
    
    def diff(self):
        return self.run("git diff --stat")
    
    def auto_commit(self, message, branch="main", email=None, name=None, remote_url=None):
        if remote_url:
            self.set_remote(remote_url)
        if email and name:
            self.set_identity(email, name)
        
        print("Staging files...")
        self.add_all()
        
        print("Creating commit...")
        result = self.commit(message)
        if not result:
            return False
        
        print("Pushing to remote...")
        self.push(branch)
        
        print("Done!")
        return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python github_commit.py <commit_message> [remote_url] [branch]")
        print("       python github_commit.py --status")
        print("       python github_commit.py --log [n]")
        sys.exit(1)
    
    git = GitHubCommit()
    
    if sys.argv[1] == "--status":
        print(git.status())
    elif sys.argv[1] == "--log":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        print(git.log(n))
    elif sys.argv[1] == "--diff":
        print(git.diff())
    else:
        message = sys.argv[1]
        remote_url = sys.argv[2] if len(sys.argv) > 2 else None
        branch = sys.argv[3] if len(sys.argv) > 3 else "main"
        
        git.auto_commit(message, branch, remote_url=remote_url)


if __name__ == "__main__":
    main()
