#!/usr/bin/env python3
"""
Name: git_repo_manager.py
Date: 2025-02-23
Purpose: A Python module that provides functionality to create or modify a Git repository for any user-specified file(s),
         including various version control features.
Function: This module defines the GitRepoManager class with methods to:
            - Check for Git installation.
            - Ensure required file paths exist.
            - Initialize a Git repository.
            - Add files, commit changes, and push to remotes.
            - Display commit logs, diffs, list and switch branches.
            - Add/update remote repository settings.
         It also offers a command-line interface with subcommands for both interactive and modular operations.
Inputs:
    - repo_path: The directory path for the Git repository.
    - tracked_files: A list (or comma-separated string) of file names (relative to the repo) to track.
    - branch: The branch name to use (default is "main").
    - commit_message: (Optional) Custom commit message.
    - Other parameters for remote management and branch switching.
Outputs:
    - A Git repository with version control enabled for the specified file(s).
Description: This module can be imported into another script or run directly via the command line. When run directly,
             it provides both an interactive mode (via the "interactive" subcommand) and various modular subcommands
             (such as "init", "add", "commit", "status", "push", "log", "diff", "list-branches", "switch-branch", and "add-remote").
File Path: ./git_repo_manager.py
"""

import os
import subprocess
import sys
import datetime
import logging
import argparse
from typing import List, Union

class GitRepoManager:
    """
    GitRepoManager manages a Git repository for one or more user-specified files.
    """

    def __init__(self, repo_path: str, tracked_files: Union[List[str], str], branch: str = "main"):
        """
        Initialize the GitRepoManager with repository path, file(s) to track, and branch.

        Args:
            repo_path (str): The path to the Git repository.
            tracked_files (Union[List[str], str]): A list or a single string of file names (relative to repo_path) to track.
            branch (str, optional): The branch name to use. Defaults to "main".
        """
        self.repo_path = os.path.abspath(repo_path)
        if isinstance(tracked_files, str):
            # Allow passing comma-separated strings as well.
            self.tracked_files = [f.strip() for f in tracked_files.split(",") if f.strip()]
        else:
            self.tracked_files = tracked_files
        self.branch = branch

    def check_git_installed(self) -> None:
        """
        Verify that Git is installed by running 'git --version'.
        Exits if Git is not installed.
        """
        try:
            output = subprocess.check_output(["git", "--version"], stderr=subprocess.STDOUT)
            logging.info("Git found: %s", output.decode().strip())
        except (subprocess.CalledProcessError, FileNotFoundError):
            logging.error("Git is not installed or not functioning properly. Please install Git and try again.")
            sys.exit(1)

    def ensure_repo_path(self) -> None:
        """
        Ensure the repository path exists; create it if it does not.
        """
        if not os.path.exists(self.repo_path):
            logging.info("Repository path '%s' does not exist. Creating it...", self.repo_path)
            try:
                os.makedirs(self.repo_path)
                logging.info("Repository path created successfully.")
            except Exception as e:
                logging.error("Failed to create repository path: %s", e)
                sys.exit(1)
        else:
            logging.info("Repository path '%s' already exists.", self.repo_path)

    def ensure_tracked_files(self) -> None:
        """
        Ensure that all tracked files exist in the repository.
        For any file that does not exist, an empty file is created.
        """
        for file_name in self.tracked_files:
            file_path = os.path.join(self.repo_path, file_name)
            if not os.path.exists(file_path):
                logging.info("File '%s' does not exist. Creating an empty file...", file_path)
                try:
                    with open(file_path, 'w') as f:
                        f.write("")  # Create an empty file.
                    logging.info("File '%s' created successfully.", file_path)
                except Exception as e:
                    logging.error("Failed to create file '%s': %s", file_path, e)
                    sys.exit(1)
            else:
                logging.info("File '%s' exists.", file_path)

    def is_git_repo(self) -> bool:
        """
        Check if the repository path is a Git repository.

        Returns:
            bool: True if a .git directory exists, False otherwise.
        """
        return os.path.isdir(os.path.join(self.repo_path, ".git"))

    def initialize_repo(self) -> None:
        """
        Initialize a new Git repository (if not already initialized) and set the default branch.
        """
        if not self.is_git_repo():
            logging.info("Initializing a new Git repository...")
            try:
                subprocess.check_call(["git", "init", self.repo_path])
                subprocess.check_call(["git", "-C", self.repo_path, "checkout", "-b", self.branch])
                logging.info("Git repository initialized with branch '%s'.", self.branch)
            except subprocess.CalledProcessError as e:
                logging.error("Failed to initialize Git repository: %s", e)
                sys.exit(1)
        else:
            logging.info("Git repository already exists at '%s'.", self.repo_path)

    def add_files(self) -> None:
        """
        Add the tracked file(s) to the Git staging area.
        """
        for file_name in self.tracked_files:
            file_path = os.path.join(self.repo_path, file_name)
            try:
                subprocess.check_call(["git", "-C", self.repo_path, "add", file_path])
                logging.info("Added '%s' to the staging area.", file_path)
            except subprocess.CalledProcessError as e:
                logging.error("Failed to add file '%s' to Git: %s", file_path, e)
                sys.exit(1)

    def commit_changes(self, commit_message: str = None) -> None:
        """
        Commit staged changes using a custom or default commit message.

        Args:
            commit_message (str, optional): Custom commit message. Defaults to a timestamped message.
        """
        if commit_message is None:
            commit_message = f"Update tracked files on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        try:
            subprocess.check_call(["git", "-C", self.repo_path, "commit", "-m", commit_message])
            logging.info("Changes committed with message: '%s'", commit_message)
        except subprocess.CalledProcessError as e:
            logging.error("Failed to commit changes: %s", e)
            sys.exit(1)

    def check_status(self) -> None:
        """
        Display the current Git repository status.
        """
        try:
            status = subprocess.check_output(["git", "-C", self.repo_path, "status"], stderr=subprocess.STDOUT)
            logging.info("Git status:\n%s", status.decode())
        except subprocess.CalledProcessError as e:
            logging.error("Failed to retrieve Git status: %s", e)
            sys.exit(1)

    def push_to_remote(self, remote_name: str = "origin", branch: str = None) -> None:
        """
        Push committed changes to a remote repository.

        Args:
            remote_name (str): The remote repository name. Defaults to "origin".
            branch (str, optional): The branch to push; defaults to the manager's branch.
        """
        if branch is None:
            branch = self.branch
        try:
            subprocess.check_call(["git", "-C", self.repo_path, "push", remote_name, branch])
            logging.info("Pushed changes to remote '%s' on branch '%s'.", remote_name, branch)
        except subprocess.CalledProcessError as e:
            logging.error("Failed to push changes to remote: %s", e)
            sys.exit(1)

    def log_history(self) -> None:
        """
        Display the commit log (in one-line format).
        """
        try:
            output = subprocess.check_output(["git", "-C", self.repo_path, "log", "--oneline"], stderr=subprocess.STDOUT)
            logging.info("Git log history:\n%s", output.decode())
        except subprocess.CalledProcessError as e:
            logging.error("Error retrieving git log: %s", e)
            sys.exit(1)

    def diff_files(self) -> None:
        """
        Display the diff of the tracked files.
        """
        try:
            output = subprocess.check_output(["git", "-C", self.repo_path, "diff"], stderr=subprocess.STDOUT)
            logging.info("Git diff:\n%s", output.decode())
        except subprocess.CalledProcessError as e:
            logging.error("Error retrieving git diff: %s", e)
            sys.exit(1)

    def list_branches(self) -> None:
        """
        List all branches in the repository.
        """
        try:
            output = subprocess.check_output(["git", "-C", self.repo_path, "branch"], stderr=subprocess.STDOUT)
            logging.info("Branches:\n%s", output.decode())
        except subprocess.CalledProcessError as e:
            logging.error("Error listing branches: %s", e)
            sys.exit(1)

    def switch_branch(self, branch: str) -> None:
        """
        Switch to the specified branch (or create it if necessary).

        Args:
            branch (str): The branch name to switch to.
        """
        try:
            subprocess.check_call(["git", "-C", self.repo_path, "checkout", branch])
            logging.info("Switched to branch '%s'.", branch)
        except subprocess.CalledProcessError as e:
            logging.error("Error switching to branch '%s': %s", branch, e)
            sys.exit(1)

    def add_remote(self, remote_name: str, remote_url: str) -> None:
        """
        Add or update a remote repository.

        Args:
            remote_name (str): The remote name.
            remote_url (str): The URL of the remote repository.
        """
        try:
            existing = subprocess.check_output(["git", "-C", self.repo_path, "remote"], stderr=subprocess.STDOUT)
            remotes = existing.decode().split()
            if remote_name in remotes:
                subprocess.check_call(["git", "-C", self.repo_path, "remote", "set-url", remote_name, remote_url])
                logging.info("Updated remote '%s' with URL: %s", remote_name, remote_url)
            else:
                subprocess.check_call(["git", "-C", self.repo_path, "remote", "add", remote_name, remote_url])
                logging.info("Added remote '%s' with URL: %s", remote_name, remote_url)
        except subprocess.CalledProcessError as e:
            logging.error("Error managing remote '%s': %s", remote_name, e)
            sys.exit(1)

def interactive_mode() -> None:
    """
    Run the module in interactive mode.
    Prompts the user for repository details and provides a menu for additional Git operations.
    """
    repo_path = input("Enter the repository path: ").strip()
    files_input = input("Enter the file(s) to track (comma-separated): ").strip()
    tracked_files = [f.strip() for f in files_input.split(",") if f.strip()]
    branch = input("Enter the branch name (default 'main'): ").strip() or "main"
    commit_message = input("Enter a commit message (or leave blank for default): ").strip() or None

    manager = GitRepoManager(repo_path, tracked_files, branch)
    manager.check_git_installed()
    manager.ensure_repo_path()
    manager.ensure_tracked_files()
    manager.initialize_repo()

    # Interactive operations menu
    while True:
        print("\nSelect an operation:")
        print("1. Add files")
        print("2. Commit changes")
        print("3. Check status")
        print("4. Push to remote")
        print("5. Show commit log")
        print("6. Show diff")
        print("7. List branches")
        print("8. Switch branch")
        print("9. Add/Update remote")
        print("0. Exit")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            manager.add_files()
        elif choice == "2":
            msg = input("Enter commit message (or leave blank for default): ").strip() or None
            manager.commit_changes(msg)
        elif choice == "3":
            manager.check_status()
        elif choice == "4":
            remote_name = input("Enter remote name (default 'origin'): ").strip() or "origin"
            manager.push_to_remote(remote_name)
        elif choice == "5":
            manager.log_history()
        elif choice == "6":
            manager.diff_files()
        elif choice == "7":
            manager.list_branches()
        elif choice == "8":
            new_branch = input("Enter the branch name to switch to: ").strip()
            if new_branch:
                manager.switch_branch(new_branch)
        elif choice == "9":
            remote_name = input("Enter remote name: ").strip()
            remote_url = input("Enter remote URL: ").strip()
            if remote_name and remote_url:
                manager.add_remote(remote_name, remote_url)
        elif choice == "0":
            print("Exiting interactive mode.")
            break
        else:
            print("Invalid choice. Please try again.")

def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Git Repository Manager Module")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    subparsers = parser.add_subparsers(dest="command", help="Subcommands for modular operations")

    # Interactive mode subcommand (new branch of functionality)
    subparsers.add_parser("interactive", help="Run in interactive mode")

    # 'init' command: Initialize repository with tracked files.
    init_parser = subparsers.add_parser("init", help="Initialize repository with tracked files")
    init_parser.add_argument("repo_path", help="Repository path")
    init_parser.add_argument("tracked_files", help="Comma-separated list of files to track")
    init_parser.add_argument("--branch", default="main", help="Branch name (default 'main')")

    # 'add' command: Add files to staging area.
    add_parser = subparsers.add_parser("add", help="Add tracked files to staging area")
    add_parser.add_argument("repo_path", help="Repository path")
    add_parser.add_argument("tracked_files", help="Comma-separated list of files to add")

    # 'commit' command: Commit changes.
    commit_parser = subparsers.add_parser("commit", help="Commit changes with a commit message")
    commit_parser.add_argument("repo_path", help="Repository path")
    commit_parser.add_argument("--message", help="Commit message", default=None)

    # 'status' command: Check repository status.
    status_parser = subparsers.add_parser("status", help="Check repository status")
    status_parser.add_argument("repo_path", help="Repository path")

    # 'push' command: Push changes to remote.
    push_parser = subparsers.add_parser("push", help="Push changes to remote")
    push_parser.add_argument("repo_path", help="Repository path")
    push_parser.add_argument("--remote", default="origin", help="Remote name (default 'origin')")
    push_parser.add_argument("--branch", default=None, help="Branch to push (default to manager branch)")

    # 'log' command: Show commit log.
    log_parser = subparsers.add_parser("log", help="Show commit log history")
    log_parser.add_argument("repo_path", help="Repository path")

    # 'diff' command: Show diff of changes.
    diff_parser = subparsers.add_parser("diff", help="Show diff of changes")
    diff_parser.add_argument("repo_path", help="Repository path")

    # 'list-branches' command: List all branches.
    list_branches_parser = subparsers.add_parser("list-branches", help="List all branches")
    list_branches_parser.add_argument("repo_path", help="Repository path")

    # 'switch-branch' command: Switch branch.
    switch_branch_parser = subparsers.add_parser("switch-branch", help="Switch to a different branch")
    switch_branch_parser.add_argument("repo_path", help="Repository path")
    switch_branch_parser.add_argument("branch", help="Branch name to switch to")

    # 'add-remote' command: Add or update remote repository.
    add_remote_parser = subparsers.add_parser("add-remote", help="Add or update remote repository")
    add_remote_parser.add_argument("repo_path", help="Repository path")
    add_remote_parser.add_argument("remote_name", help="Remote name")
    add_remote_parser.add_argument("remote_url", help="Remote URL")

    return parser.parse_args()

def main() -> None:
    """
    Main function for the command-line interface.
    """
    args = parse_arguments()
    # Set logging level based on the verbose flag.
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="[%(levelname)s] %(message)s")

    # If no subcommand is provided, default to interactive mode.
    if args.command == "interactive" or args.command is None:
        interactive_mode()
    elif args.command == "init":
        manager = GitRepoManager(args.repo_path, args.tracked_files, args.branch)
        manager.check_git_installed()
        manager.ensure_repo_path()
        manager.ensure_tracked_files()
        manager.initialize_repo()
    elif args.command == "add":
        manager = GitRepoManager(args.repo_path, args.tracked_files)
        manager.add_files()
    elif args.command == "commit":
        manager = GitRepoManager(args.repo_path, [])
        manager.commit_changes(args.message)
    elif args.command == "status":
        manager = GitRepoManager(args.repo_path, [])
        manager.check_status()
    elif args.command == "push":
        manager = GitRepoManager(args.repo_path, [])
        manager.push_to_remote(args.remote, args.branch)
    elif args.command == "log":
        manager = GitRepoManager(args.repo_path, [])
        manager.log_history()
    elif args.command == "diff":
        manager = GitRepoManager(args.repo_path, [])
        manager.diff_files()
    elif args.command == "list-branches":
        manager = GitRepoManager(args.repo_path, [])
        manager.list_branches()
    elif args.command == "switch-branch":
        manager = GitRepoManager(args.repo_path, [])
        manager.switch_branch(args.branch)
    elif args.command == "add-remote":
        manager = GitRepoManager(args.repo_path, [])
        manager.add_remote(args.remote_name, args.remote_url)
    else:
        logging.error("Invalid command. Use -h for help.")
        sys.exit(1)

if __name__ == "__main__":
    main()
