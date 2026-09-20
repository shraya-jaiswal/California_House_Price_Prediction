import subprocess
import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


WAIT_SECONDS = 10
timer = None
lock = threading.Lock()


def upload_to_github():
    global timer

    print("\nChecking for changes...")

    with lock:
        timer = None

    # Add all new and modified files
    subprocess.run(["git", "add", "."], check=True)

    # Check if anything is staged
    result = subprocess.run(
        ["git", "diff", "--cached", "--quiet"]
    )

    if result.returncode == 0:
        print("No changes to upload.")
        return

    print("Uploading changes to GitHub...")

    subprocess.run(
        ["git", "commit", "-m", "Automatic update"],
        check=True
    )

    subprocess.run(
        ["git", "push"],
        check=True
    )

    print("✓ Changes uploaded to GitHub!")


def schedule_upload():
    global timer

    with lock:

        if timer is not None:
            timer.cancel()

        timer = threading.Timer(
            WAIT_SECONDS,
            upload_to_github
        )

        timer.start()


class GitAutoPush(FileSystemEventHandler):

    def on_any_event(self, event):

        if event.is_directory:
            return

        path = event.src_path.replace("\\", "/")

        # Ignore Git's internal files
        if "/.git/" in path:
            return

        # Ignore Python virtual environments
        if "/venv/" in path or "/.venv/" in path:
            return

        print("Change detected.")
        schedule_upload()


# -------------------------------------------------
# Upload existing changes when the program starts
# -------------------------------------------------

print("========================================")
print("       GitHub Auto Upload Running")
print("========================================")
print()
print("Checking for existing changes...")

upload_to_github()

print()
print("Now watching the entire project...")
print("New files will also be uploaded.")
print("Waiting 10 seconds after your last change.")
print("Press Ctrl+C to stop.")
print()


# -------------------------------------------------
# Watch the project for future changes
# -------------------------------------------------

observer = Observer()

observer.schedule(
    GitAutoPush(),
    ".",
    recursive=True
)

observer.start()


try:
    while True:
        time.sleep(1)

except KeyboardInterrupt:

    with lock:
        if timer is not None:
            timer.cancel()

    observer.stop()

observer.join()