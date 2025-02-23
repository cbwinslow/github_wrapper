#!/usr/bin/env python3
"""
Name: git_repo_manager.py
Date: 2025-02-23
Purpose: A Python module that provides functionality to create or modify a Git repository for any user-specified file(s),
         including version control features.
Function: The module defines the GitRepoManager class with methods for checking Git installation, ensuring file paths exist,
          initializing a Git repository, adding files, committing changes, and pushing to remote repositories.
Inputs:
    - repo_path: The directory path for the Git repository.
    - tracked_files: A list (or a single string) of file names (relative to the repo) to track under version control.
    - commit_message: (Optional) A custom commit message.
Outputs:
    - A Git repository in repo_path with version control enabled for the specified file(s).
Description: This module can be imported and its features accessed via the GitRepoManager class and the run_manager() helper function.
File Path: ./git_repo_manager.py
"""

import os
import subprocess
import sys
import datetime
from typing import List, Union

class GitRepoManager:
    """
    GitRepoManager manages a Git repository for one or more user-specified files.
    """

    def __init__(self, repo_path: str, tracked_files: Union[List[str], str], branch: str = "main"):
        """
        Initialize the GitRepoManager with the repository path, file(s) to track, and branch name.

        Args:
            repo_path (str): The path to the Git repository.
            tracked_files (Union[List[str], str]): A list or single string of file names (relative to repo_path) to track.
            branch (str, optional): The default branch name. Defaults to "main".
        """
        self.repo_path = os.path.abspath(repo_path)
        if isinstance(tracked_files, str):
            self.tracked_files = [tracked_files]
        else:
            self.tracked_files = tracked_files
        self.branch = branch

    def check_git_installed(self) -> None:
        """
        Check if Git is installed by running 'git --version'.
        Exits the program if Git is not installed.
        """
        try:
            output = subprocess.check_output(["git", "--version"], stderr=subprocess.STDOUT)
            print(f"[INFO] Git found: {output.decode().strip()}")
        except subprocess.CalledProcessError:
            print("[ERROR] Git is not installed or not functioning properly. Please install Git and try again.")
            sys.exit(1)
        except FileNotFoundError:
            print("[ERROR] Git is not installed. Please install Git and try again.")
            sys.exit(1)

    def ensure_repo_path(self) -> None:
        """
        Ensure that the repository path exists. Create the directory if it does not exist.
        """
        if not os.path.exists(self.repo_path):
            print(f"[INFO] Repository path '{self.repo_path}' does not exist. Creating it...")
            try:
                os.makedirs(self.repo_path)
                print("[INFO] Repository path created successfully.")
            except Exception as e:
                print(f"[ERROR] Failed to create repository path: {e}")
                sys.exit(1)
        else:
            print(f"[INFO] Repository path '{self.repo_path}' already exists.")

    def ensure_tracked_files(self) -> None:
        """
        Ensure that all tracked files exist in the repository.
        For any file that does not exist, create an empty file.
        """
        for file_name in self.tracked_files:
            file_path = os.path.join(self.repo_path, file_name)
            if not os.path.exists(file_path):
                print(f"[INFO] File '{file_path}' does not exist. Creating an empty file...")
                try:
                    # Create the file and write an empty string.
                    with open(file_path, 'w') as f:
                        f.write("")
                    print(f"[INFO] File '{file_path}' created successfully.")
                except Exception as e:
                    print(f"[ERROR] Failed to create file '{file_path}': {e}")
                    sys.exit(1)
            else:
                print(f"[INFO] File '{file_path}' exists.")

    def is_git_repo(self) -> bool:
        """
        Check whether the repository path is already a Git repository.

        Returns:
            bool: True if a .git directory exists, False otherwise.
        """
        return os.path.isdir(os.path.join(self.repo_path, ".git"))

    def initialize_repo(self) -> None:
        """
        Initialize a new Git repository if one is not already present and set the default branch.
        """
        if not self.is_git_repo():
            print("[INFO] Initializing a new Git repository...")
            try:
                subprocess.check_call(["git", "init", self.repo_path])
                subprocess.check_call(["git", "-C", self.repo_path, "checkout", "-b", self.branch])
                print("[INFO] Git repository initialized successfully.")
            except subprocess.CalledProcessError as e:
                print(f"[ERROR] Failed to initialize Git repository: {e}")
                sys.exit(1)
        else:
            print("[INFO] Git repository already exists.")

    def add_files(self) -> None:
        """
        Add the tracked file(s) to the Git staging area.
        """
        for file_name in self.tracked_files:
            file_path = os.path.join(self.repo_path, file_name)
            try:
                subprocess.check_call(["git", "-C", self.repo_path, "add", file_path])
                print(f"[INFO] Added '{file_path}' to the staging area.")
            except subprocess.CalledProcessError as e:
                print(f"[ERROR] Failed to add file '{file_path}' to Git: {e}")
                sys.exit(1)

    def commit_changes(self, commit_message: str = None) -> None:
        """
        Commit staged changes to the repository using a custom or default commit message.

        Args:
            commit_message (str, optional): Custom commit message. If None, a default message with a timestamp is used.
        """
        if commit_message is None:
            commit_message = f"Update tracked files on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        try:
            subprocess.check_call(["git", "-C", self.repo_path, "commit", "-m", commit_message])
            print("[INFO] Changes committed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to commit changes: {e}")
            sys.exit(1)

    def check_status(self) -> None:
        """
        Display the current status of the Git repository.
        """
        try:
            status = subprocess.check_output(["git", "-C", self.repo_path, "status"], stderr=subprocess.STDOUT)
            print("[INFO] Current Git status:")
            print(status.decode())
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to retrieve Git status: {e}")
            sys.exit(1)

    def push_to_remote(self, remote_name: str = "origin", branch: str = None) -> None:
        """
        Push committed changes to a remote repository.

        Args:
            remote_name (str): The remote repository name. Default is "origin".
            branch (str, optional): The branch to push. Defaults to the manager's branch if not provided.
        """
        if branch is None:
            branch = self.branch
        try:
            subprocess.check_call(["git", "-C", self.repo_path, "push", remote_name, branch])
            print(f"[INFO] Changes pushed to remote '{remote_name}/{branch}' successfully.")
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to push changes to remote: {e}")
            sys.exit(1)

def run_manager(repo_path: str, tracked_files: Union[List[str], str], commit_message: str = None, branch: str = "main") -> None:
    """
    Convenience function that creates a GitRepoManager instance and executes the full workflow.

    Args:
        repo_path (str): The directory path for the Git repository.
        tracked_files (Union[List[str], str]): A list or single string of file names (relative to repo_path) to track.
        commit_message (str, optional): Custom commit message. Defaults to None.
        branch (str, optional): The branch name to use. Defaults to "main".
    """
    manager = GitRepoManager(repo_path, tracked_files, branch)
    manager.check_git_installed()
    manager.ensure_repo_path()
    manager.ensure_tracked_files()
    manager.initialize_repo()
    manager.add_files()
    manager.commit_changes(commit_message)
    manager.check_status()

def main():
    """
    Main function for running the module as a standalone script.
    Modify the variables below as needed.
    """
    # Define variables for paths and file names.
    REPO_PATH = "./my_repo"             # Repository directory (modify as needed)
    TRACKED_FILES = ["file1.txt", "file2.conf"]  # List (or single string) of file names to track
    COMMIT_MESSAGE = None                # Custom commit message (None for default behavior)

    run_manager(REPO_PATH, TRACKED_FILES, COMMIT_MESSAGE)

# This conditional ensures that the module can be imported without running the main function.
if __name__ == "__main__":
    main()
