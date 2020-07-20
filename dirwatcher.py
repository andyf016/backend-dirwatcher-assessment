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
    This is a handler for SIGTERM and SIGINT. Other signals can be mapped
    here as well (SIGHUP?) Basically, it just sets a global flag, and
    main() will exit its loop if the signal is trapped. :param sig_num:
    The integer signal number that was trapped from the OS. :param frame:
    Not used :return None
    """
    global exit_flag
    # log the associated signal name
    logger.warning('Received ' + signal.Signals(sig_num).name)
    exit_flag = True


def scan_single_file(path, magic_word):
    """
    scans each file in the dictionary of files for the magic string
    and then keeps track of the last line read by updating the value
    of the document in the dictionary
    """
    for key in file_dict.keys():
        current_value = file_dict.get(key)
        key_path = os.path.join(path, key)
        with open(key_path, 'r') as f:
            line_list = f.readlines()
            for i, line in enumerate(line_list[current_value:]):
                result = line.find(magic_word)
                if result != -1:
                    logger.info(f"""Found magic string on line
                                {i + current_value + 1} in {key}""")
            file_dict[key] = current_value + (len(line_list) - current_value)
    return


def detect_added_files(dir_list, ext):
    """
    Scans list of items in directory and compares them to the current
    dictionary of files adding items that are not on the list and have
    the correct extension
    """
    for item in dir_list:
        if item in file_dict.keys():
            pass
        elif item.endswith(ext):
            logger.info(f'{item} has been found!')
            file_dict[item] = 0
    return



def detect_removed_files(dir_list):
    """
    Compares items in a list of keys of the current file dictionary
    with items in the updated file list and removes keys that are not
    on the updated list.
    """
    for item in file_dict.keys():
        if item not in dir_list:
            logger.info(f'{item} has been removed')
            file_dict.pop(item)
    return


def dir_watching(path, dir_list, ext):
    """
    watches the given directory by implementing the two detect functions
    passes these functions the path, updated directory list and the
    extension to search for
    """
    detect_added_files(dir_list, ext)
    detect_removed_files(dir_list)
    return


def create_parser():
    parser = argparse.ArgumentParser(
        description=""" This program will monitor a given directory for text files
            that are created within the monitored directory and will
            continually search within all files in the directory for a
            "magic string", which is provided as a command line argument""")
    parser.add_argument('path', nargs='+', type=str,
                        help='directory path to watch')
    parser.add_argument('magic', nargs='+', type=str,
                        help='string to watch for')
    parser.add_argument('-e', '--ext',
                        help='file extension to watch')
    parser.add_argument('-i', '--interval', type=int,
                        help='Number of seconds between polling')
    return parser


def main(args):
    """
    Main function, contains banners for beginning and end of run
    contains the try except process and the polling interval
    """
    parser = create_parser()
    name_space = parser.parse_args(args)
    # Hook into these two signals from the OS
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    # Now my signal_handler will get called if OS sends
    # either of these to my process.

    # set start time
    app_start_time = datetime.datetime.now()
    # set path name and magic string
    path = ''.join(name_space.path)
    magic = ''.join(name_space.magic)
    # set extension and default if none is provided
    if name_space.ext:
        ext = name_space.ext
    else:
        ext = ('.md', '.txt')
    # set polling interval, defaults to 5 seconds
    if name_space.interval:
        polling_interval = name_space.interval
    else:
        polling_interval = 5
    # logging banner adapted from Piero's logging demo
    logger.info(
        '\n'
        '---------------------------------------------------------------\n'
        f'      Running{__file__}\n'
        f'      In: {path}                                              \n'
        f'      Started on {app_start_time.isoformat()}\n'
        '---------------------------------------------------------------\n'
        )
    while not exit_flag:
        try:
            dir_list = os.listdir(path=path)
            dir_watching(path, dir_list, ext)
            scan_single_file(path, magic)
        except RuntimeError:
            # This error was coming up when the file dict was modified
            # Specifically the dictionary changing size during iteration.
            pass
        except IOError:
            logger.error(" IO Error Directory or file not found")
            # This nested try/except statement is to catch when
            # a directory has been removed and alert the user that
            # the watched files in the directory have been deleted
            # as is implied when a directory is deleted
            try:
                dir_list.clear()
                detect_removed_files(dir_list)
            except Exception:
                pass
        except FileNotFoundError:
            logger.error("Directory or file not found")
        except Exception as e:
            # This is an UNHANDLED exception
            logger.error(f" {e} What happened!?")
        # put a sleep inside my while loop so I don't peg the cpu usage at 100%
        time.sleep(polling_interval)
    # set uptime
    uptime = datetime.datetime.now() - app_start_time
    logger.info(
        '\n'
        '-------------------------------------------------------------------\n'
        f'      Stopped {__file__}\n'
        f'      Uptime was {str(uptime)}\n'
        '-------------------------------------------------------------------\n'
        )


if __name__ == '__main__':
    main(sys.argv[1:])
