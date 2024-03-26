import multiprocessing
import time

def worker(event):
    while not event.is_set():
        print("Working...")
        # Add your processing code here
        time.sleep(1)  # Simulating some work

if __name__ == '__main__':
    stop_event = multiprocessing.Event()
    p1 = multiprocessing.Process(target=worker, args=(stop_event,))
    p2 = multiprocessing.Process(target=worker, args=(stop_event,))

    p1.start()
    p2.start()

    # Let the processes run for a while
    # For example, let them run for 5 seconds
    multiprocessing.Process(target=time.sleep, args=(5,)).start()

    # Set the event to stop the processes
    stop_event.set()

    # Wait for processes to finish
    p1.join()
    p2.join()

    print("All processes stopped.")
