import argparse
import logging
import logging.handlers
import signal
import time
import datetime
import os
import sys

file_dict = {}

exit_flag = False

logger = logging.getLogger(__name__)

# configure logging output, thanks Piero!
logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(name)-12s \
            %(levelname)-8s [%(threadName)-12s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.DEBUG
)

# set logging level
logger.setLevel(logging.DEBUG)


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
    logger.warning('Received ' + signal.Signals(sig_num).name)
    exit_flag = True


def scan_single_file(file, magic_word):
    current_value = file_dict.get(file)
    with open(file, 'r') as f:
        line_list = f.readlines()
        for line in line_list[current_value:]:
            result = line.find(magic_word)
            if result != -1:
                logger.info(f'Found magic string on line \
                            {line_list.index(line) + 1}')
        file_dict[file] = current_value + (len(line_list) - current_value)
        return

def detect_added_files(file_dict, dir_list):
    for item in dir_list:
        if item in file_dict.keys():
            pass
        elif os.path.isfile(item) and item.endswith(('.md', '.txt')):
            logger.info(f'{item} has been found!')
            file_dict[item] = 0
    return


def detect_removed_files(file_dict, dir_list):
    for item in file_dict.keys():
        if item not in dir_list:
            logger.info(f'{item} has been removed')
            file_dict.pop(item)
    return


def dir_watching():
    dir_list = os.listdir()
    detect_added_files(file_dict, dir_list)
    detect_removed_files(file_dict, dir_list)
    print(file_dict)
    return


def create_parser():
    parser = argparse.ArgumentParser(
        description=""" This program will monitor a given directory for text files
            that are created within the monitored directory and will
            continually search within all files in the directory for a
            "magic string", which is provided as a command line argument""")
    parser.add_argument('path', nargs='+', type=str, help='directory path to watch')
    # parser.add_argument('magic', nargs='+', type=str, help='string to watch for')
    parser.add_argument('-e', '--ext', help='text file extension to watch')
    parser.add_argument('-i', '--interval', type=int,
                        help='Number of seconds between polling')
    return parser


def main(args):
    parser = create_parser()
    name_space = parser.parse_args(args)
    # Hook into these two signals from the OS
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    # Now my signal_handler will get called if OS sends
    # either of these to my process.

    # set start time
    app_start_time = datetime.datetime.now()
    path = ''.join(name_space.path)
    # magic_str = ''.join(name_space.magic)
    # if not name_space:
    #     parser.print_usage()
    #     sys.exit(1)

    if name_space.interval:
        polling_interval = name_space.interval
    else:
        polling_interval = 5
    # logging banner adapted from Piero's logging demo
    logger.info(
        '\n'
        '---------------------------------------------------------------\n'
        f'      Running{__file__}\n'
        f'      Started on {app_start_time.isoformat()}\n'
        '---------------------------------------------------------------\n'
        )
    while not exit_flag:
        try:
            dir_watching()
        except RuntimeError:
            pass
        except IOError:
            logger.error("Directory or file not found")
        except FileNotFoundError:
            logger.error("Directory or file not found")
        #except Exception as e:
            # This is an UNHANDLED exception
        #    logger.error(f" {e} What the hell happened!?")
        #    pass

        # put a sleep inside my while loop so I don't peg the cpu usage at 100%
        time.sleep(polling_interval)
    uptime = datetime.datetime.now() - app_start_time
    logger.info(
        '\n'
        '-------------------------------------------------------------------\n'
        f'      Stopped {__file__}\n'
        f'      Uptime was {str(uptime)}\n'
        '-------------------------------------------------------------------\n'
        )

    # final exit point happens here
    # Log a message that we are shutting down
    # Include the overall uptime since program start


if __name__ == '__main__':
    main(sys.argv[1:])