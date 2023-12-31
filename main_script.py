import psutil
import threading
import time
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("script.log")
    ]
)

terminate_flag = False

def get_disk_speed(interval=1):
    initial_disk_usage = psutil.disk_io_counters()
    time.sleep(interval)
    final_disk_usage = psutil.disk_io_counters()

    read_speed = (final_disk_usage.read_bytes - initial_disk_usage.read_bytes) / interval
    write_speed = (final_disk_usage.write_bytes - initial_disk_usage.write_bytes) / interval

    return read_speed, write_speed

def generate_sequences(start, target, num_characters, file_name):
    sequences = []

    def generate_recursive(prefix, remaining_characters):
        if terminate_flag:
            return

        if remaining_characters == 0:
            sequences.append(prefix)
            return
        for i in range(ord(start), ord(target) + 1):
            generate_recursive(prefix + chr(i), remaining_characters - 1)

    generate_recursive('', num_characters)

    if file_name:
        with open(file_name, 'w') as output_file:
            for seq in sequences:
                output_file.write(seq + '\n')

def detect_and_terminate(threshold_write_speed, start, target, num_characters, file_name):
    try:
        while not terminate_flag:
            _, write_speed = get_disk_speed()
            logging.info(f"Current write speed: {write_speed} B/s")

            if write_speed > threshold_write_speed:
                logging.warning(f"High disk I/O speed ({write_speed} B/s). Terminating script.")
                os._exit(0)

            time.sleep(1)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    logging.info("Warning You Can't Use Ctrl+C!")
    logging.info("Program started.")
    start = '0'
    target = 'z'
    num_characters = 5
    file_name = 'many.txt'
    threshold_write_speed = 6000000

    generate_sequences_thread = threading.Thread(target=generate_sequences, args=(start, target, num_characters, file_name))
    disk_detection_thread = threading.Thread(target=detect_and_terminate, args=(threshold_write_speed, start, target, num_characters, file_name))

    disk_detection_thread.daemon = True

    generate_sequences_thread.start()
    disk_detection_thread.start()

    generate_sequences_thread.join()

    logging.info("Main script completed.")
