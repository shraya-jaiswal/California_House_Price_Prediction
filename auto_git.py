import subprocess
import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


WAIT_SECONDS = 10

timer = None
lock = threading.Lock()


def upload_to_github():
    print("\nChanges detected. Waiting for more changes...")

    time.sleep(WAIT_SECONDS)

    with lock:
        global timer
        timer = None

    print("Uploading changes to GitHub...")

    subprocess.run(["git", "add", "."], check=True)

    # Check whether there are actually changes to commit
    result = subprocess.run(
        ["git", "diff", "--cached", "--quiet"]
    )

    if result.returncode == 0:
        print("No changes to commit.")
        return

    subprocess.run(
        ["git", "commit", "-m", "Automatic update"],
        check=True
    )

    subprocess.run(
        ["git", "push"],
        check=True
    )

    print("✓ Changes uploaded to GitHub!")


class GitAutoPush(FileSystemEventHandler):

    def on_any_event(self, event):
        if event.is_directory:
            return

        path = event.src_path.replace("\\", "/")

        # Ignore Git and virtual environments
        if "/.git/" in path:
            return

        if "/venv/" in path or "/.venv/" in path:
            return

        global timer

        with lock:

            # Cancel previous timer
            if timer is not None:
                timer.cancel()

            # Start a new timer
            timer = threading.Timer(
                WAIT_SECONDS,
                upload_to_github
            )

            timer.start()


observer = Observer()

observer.schedule(
    GitAutoPush(),
    ".",
    recursive=True
)

observer.start()

print("========================================")
print("      GitHub Auto Upload Running")
print("========================================")
print()
print("Watching the entire project...")
print("New files will also be uploaded.")
print("Waiting 10 seconds after your last change.")
print()
print("Press Ctrl+C to stop.")
print()

try:
    while True:
        time.sleep(1)

except KeyboardInterrupt:

    if timer is not None:
        timer.cancel()

    observer.stop()

observer.join()