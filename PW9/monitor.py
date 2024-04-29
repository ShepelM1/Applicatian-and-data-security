import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class EventHandler(FileSystemEventHandler):
    def __init__(self, log_file):
        super().__init__()
        self.log_file = log_file
        self.last_analyzed_times = {}

    def on_any_event(self, event):
        event_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        log_entry = f"{event_time} - {event.event_type}: {event.src_path}\n"
        with open(self.log_file, 'a') as f:
            f.write(log_entry)

        if event.is_directory:
            return

        if event.event_type == 'created' or event.event_type == 'modified':
            self.schedule_file_analysis(event.src_path)

    def schedule_file_analysis(self, file_path):
        current_time = time.time()
        if file_path not in self.last_analyzed_times or current_time - self.last_analyzed_times[file_path] >= 1:
            self.last_analyzed_times[file_path] = current_time
            analyze_file(file_path)


def analyze_file(file_path):
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
            total_lines = len(lines)
            first_lines = lines[:5]

        print(f"File: {file_path}")
        print(f"Total number of lines in the file: {total_lines}")
        print("First few lines of the file:")
        for line in first_lines:
            print(line.strip())
    except FileNotFoundError:
        print(f"File not found: {file_path}")


def monitor_directory(directory):
    log_file = 'event_log.txt'
    event_handler = EventHandler(log_file)
    observer = Observer()
    observer.schedule(event_handler, directory, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python monitor.py <directory_to_monitor>")
        sys.exit(1)

    directory = sys.argv[1]
    monitor_directory(directory)
