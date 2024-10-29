import time

class TimeoutException(Exception):
    pass


def wait_until_true_or_timeout(condition_function, time_to_wait = 10, starting_wait_time = 0.0001):
    time_waited = 0
    waiting_time = starting_wait_time
    while True:
        if condition_function():
            return True
        elif time_waited >= time_to_wait:
            raise TimeoutException(f"Timed out with time to wait {time_to_wait}!")
        else:
            time.sleep(waiting_time)
            time_waited += waiting_time
            waiting_time = min(time_to_wait - time_waited, waiting_time*2)