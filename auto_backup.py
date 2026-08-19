import os
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Folder to watch
WATCH_DIR = "/home/sparkeee/fastflags"

# Git repository path
REPO_DIR = "/home/sparkeee/projects/demstrap-backup"

class GitHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory or not event.src_path.endswith('.json'):
            return
        
        print(f"Detected change in: {event.src_path}")
        self.git_commit_push()

    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith('.json'):
            return
        
        print(f"Detected new file: {event.src_path}")
        self.git_commit_push()

    def git_commit_push(self):
        try:
            os.chdir(REPO_DIR)
            subprocess.run(["git", "add", "."])
            subprocess.run(["git", "commit", "-m", "auto: backup FastFlag config changes"])
            subprocess.run(["git", "push", "origin", "main"])
            print("Successfully pushed to GitHub.")
        except Exception as e:
            print(f"Error during git operations: {e}")

if __name__ == "__main__":
    event_handler = GitHandler()
    observer = Observer()
    observer.schedule(event_handler, path=WATCH_DIR, recursive=False)
    observer.start()

    print(f"Monitoring {WATCH_DIR} for changes...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
