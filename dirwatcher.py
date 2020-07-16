import argparse
import logging
import logging.handlers
import signal
import time
import datetime
import os
import sys

exit_flag = False

logger = logging.getLogger(__name__)

# configure logging output
logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(name)-12s \
            %(levelname)-8s [%(threadName)-12s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.DEBUG
)


def signal_handler(sig_num, frame):
    """
    This is a handler for SIGTERM and SIGINT. Other signals can be mapped here as well (SIGHUP?)
    Basically, it just sets a global flag, and main() will exit its loop if the signal is trapped.
    :param sig_num: The integer signal number that was trapped from the OS.
    :param frame: Not used
    :return None
    """
    global exit_flag
    # log the associated signal name
    logger.warn('Received ' + signal.Signals(sig_num).name)
    exit_flag = True


def dir_watching():
    pass


def create_parser():
    parser = argparse.ArgumentParser(
        description=""" This program will monitor a given directory for text files
            that are created within the monitored directory and will
            continually search within all files in the directory for a
            "magic string", which is provided as a command line argument""")
    parser.add_argument('path', help='directory path to watch')
    parser.add_argument('magic', help='string to watch for')
    parser.add_argument('-e', '--ext', help='text file extension to watch')
    parser.add_argument('-i', '--interval', type=int,
                        help='Number of seconds between polling')


def main(args):
    parser = create_parser()
    name_space = parser.parse_args(args)
    # Hook into these two signals from the OS
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    # Now my signal_handler will get called if OS sends
    # either of these to my process.

    if not name_space:
        parser.print_usage()
        sys.exit(1)

    polling_interval = name_space.i

    while not exit_flag:
        try:
            # call my directory watching function
            pass
        except Exception as e:
            # This is an UNHANDLED exception
            # Log an ERROR level message here
            pass

        # put a sleep inside my while loop so I don't peg the cpu usage at 100%
        time.sleep(polling_interval)

    # final exit point happens here
    # Log a message that we are shutting down
    # Include the overall uptime since program start


if __name__ == '__main__':
    main(sys.argv[1:])