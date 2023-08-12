from termcolor import colored as col
import time


def time_func(func):
  def wrapper(*args, **kwargs):
    start_time = time.perf_counter()
    result = func(*args, **kwargs)
    end_time = time.perf_counter()
    time_taken = end_time - start_time
    
    print(col(f'Time taken to execute {func.__name__}: {time_taken:.1f} seconds', 'light_green'))

    return result

  return wrapper
