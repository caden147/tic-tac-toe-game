import os
import datetime
import file_utilities

class Logger:
    """A logger is used to record logging messages to a log file."""
    def __init__(self, path):
        """
        path: the path to the log file.
        A file will be created at the path if one does not exist.
        """
        self.path = path
        file_utilities.create_file_at_path_if_nonexistent(path)
    
    def log_message(self, message: str):
        """
        message: the message to store in the log.
        The current timestamp is prepended to the message.
        """
        with open(self.path, "a+") as file:
            timestamp = datetime.datetime.now().strftime("%m/%d/%y %H:%M:%S.%f")
            file.write(f"{timestamp}: {message}\n")
