import time

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

