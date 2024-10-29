import time
from client import Client
from logging_utilities import PrimaryMemoryLogger

class TimeoutException(Exception):
    """An exception indicating that something timed out"""
    pass


def wait_until_true_or_timeout(condition_function, timeout_message = "", time_to_wait = 10, starting_wait_time = 0.0001):
    """
        Repeatedly checks the condition function to see if it is true. If so, the function returns True. 
        If the time_to_wait is exceeded, a TimeoutException is raised.
        The function uses sleep statements to avoid using too much CPU time.
        condition_function: the condition function to check
        timeout_message: a message to display on timeout
        time_to_wait: how many seconds to wait before timing out
        starting_wait_time: the initial amount of time to sleep in between invoking the condition function
    """
    time_waited = 0
    waiting_time = starting_wait_time
    while True:
        if condition_function():
            return True
        elif time_waited >= time_to_wait:
            raise TimeoutException(f"Timed out with time to wait {time_to_wait}! " + timeout_message)
        else:
            time.sleep(waiting_time)
            time_waited += waiting_time
            waiting_time = min(time_to_wait - time_waited, waiting_time*2)

class TestClientHandler:
    def __init__(self, host, port, selector, socket_creation_function):
        """
            Manages a client and associated data used for testing
            host: the server host address
            port: the server port address
            selector: the selector
            socket_creation_function: the socket creation function
        """
        self.logger = PrimaryMemoryLogger()
        self.output = []
        self.selector = selector
        output_text_function=lambda x: self.output.append(x)
        self.client = Client(
            host,
            port,
            selector,
            self.logger,
            output_text_function=output_text_function,
            socket_creation_function=socket_creation_function
        )
    
