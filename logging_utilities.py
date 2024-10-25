import os
import datetime
import file_utilities

class Logger:
    """A logger is used to record logging messages to a log file."""
    def __init__(self, path, *, debugging_mode: bool = True):
        """
        path: the path to the log file.
        A file will be created at the path if one does not exist.
        """
        self.path = path
        file_utilities.create_file_at_path_if_nonexistent(path)
        self.debugging_mode = debugging_mode
    
    def _convert_value_for_logging(self, value):
        value = str(value)
        return value

    def _commit_message_to_log(self, value, category):
        """Does the work of putting values in string format and storing it in the log. Uses the category as a prefix."""
        value = self._convert_value_for_logging(value)
        if category is not None:
            value += self._convert_value_for_logging(category)
        with open(self.path, "a+") as file:
            timestamp = datetime.datetime.now().strftime("%m/%d/%y %H:%M:%S.%f")
            file.write(f"{timestamp}: {value}\n")

    def log_message(self, value, category = None):
        """
        value: a value to store in the log.
        category: an optional category for the type of message.
        The current timestamp is prepended to the message.
        """
        self._commit_message_to_log(value, category)

    def handle_debug_message(self, value, category = None):
        """
            Records the information in the log if the logger is in debugging mode
            value: a value to store in the log.
            category: an optional category for the type of message.
        """
        if self.debugging_mode:
            self.log_message(value, category)

    
