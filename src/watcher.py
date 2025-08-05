"""
src/watcher.py
"""


import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from src.run_generators import generate_pdf_from_excel


WATCH_FOLDER = "data"
OUTPUT_FOLDER = "outputs"


class ExcelEventHandler(FileSystemEventHandler):

    def on_modified(self, event):

        if event.is_directory:
            return
        
        if event.src_path.endswith(".xlsx"):
            filename = os.path.basename(event.src_path)
            output_name = filename.replace(".xlsx", ".pdf")
            output_path = os.path.join(OUTPUT_FOLDER, output_name)

            # Notification
            print("\a") # BEEP!
            print(f"Detected change in: {filename}")
            generate_pdf_from_excel(event.src_path, output_path)

    def on_create(self, event):

        self.on_modified(event)


def start_watching():
    
    print(f"Watching folder: {WATCH_FOLDER}")
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    event_handler = ExcelEventHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_FOLDER, recursive=False)   
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("Watcher stopped.")

    observer.join()