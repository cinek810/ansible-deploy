"""Main module for ansible-deploy"""

import sys
import os
import argparse
import logging
import datetime
#TODO: Add an option to explicitely enable syslog logging
#from logging import handlers as log_han


LOGNAME = "ansible-deploy_execution_{}.log"
SEQUENCE_PREFIX = "SEQ"
WORKDIR = "/tmp"


def get_sub_command(command):
    """Function to check the first arguments (argv[1..]) looking for a subcommand"""
    if command == "run":
        subcommand = "run"
    else:
        logger.error("Unknown subcommand :%s", (command))
        sys.exit("55")
    return subcommand

def set_logging(log_dir: str, name: str, timestamp: str):
    """Function to create logging objects"""
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_path = os.path.join(log_dir, name.format(timestamp))

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s]: %(message)s")
    console_formatter = logging.Formatter("\n%(asctime)s [%(levelname)s]: %(message)s\n")

#   TODO: Add an option to explicitly enable syslog logging
#    rsys_handler = log_han.SysLogHandler(address="/dev/log")
#    rsys_handler.setFormatter(formatter)
#    rsys_handler.setLevel(logging.ERROR)
#    logger.addHandler(rsys_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)

    return logger


def parse_options(argv):
    """Generic function to parse options for all commands, we validate if the option was allowed for
    specific subcommand outside"""
    parser = argparse.ArgumentParser()

    parser.add_argument("--infrastructure", "-i", nargs=1, default=[None], metavar="INFRASTRUCTURE",
                        help='Specify infrastructure for deploy.')
    parser.add_argument("--stage", "-s", nargs=1, default=[None], metavar="STAGE",
                        help='Specify stage type. Available types are: "testing" and "production".')
    parser.add_argument("--commit", "-c", nargs=1, default=[None], metavar="COMMIT", help='Provide '
                        'commit ID.')
    parser.add_argument("--task", "-t", nargs=1, default=[None], metavar='"TASK NAME"',
                        help='Provide task name in "".')

    arguments = parser.parse_args(argv)

    options = {}
    options["infrastructure"] = arguments.infrastructure[0]
    options["stage"] = arguments.stage[0]
    options["commit"] = arguments.commit[0]
    options["task"] = arguments.task[0]

    return options

def create_workdir(timestamp: str, base_dir: str):
    """Function to create working directory on filesystem"""
    short_ts = timestamp.split("_")[0]
    date_dir = os.path.join(base_dir, short_ts)

    #
    #TODO: Add locking of the directory

    if short_ts not in os.listdir(base_dir):
        seq_path = os.path.join(date_dir, f"{SEQUENCE_PREFIX}0000")
    else:
        sequence_list = os.listdir(date_dir)
        sequence_list.sort()
        new_sequence = int(sequence_list[-1].split(SEQUENCE_PREFIX)[1]) + 1
        seq_path = os.path.join(date_dir, f"{SEQUENCE_PREFIX}{new_sequence:04d}")

    os.makedirs(seq_path)
    return seq_path

def validate_options(options, subcommand):
    """Function checking if the options set are allowed in this subcommand"""
    logger.debug("validate_options running for subcommand: %s", (subcommand))
    if subcommand == "run":
        if not options["task"]:
            logger.error("run requires --task")
            sys.exit(55)
    return True

def load_configuration():
    """Function responsible for reading configuration files and running a schema validator against
    it"""


def validate_user_infra_stage(user: str, infra: str):
    """Function checking if user has rights to execute command on selected infrastructure
    Required for: run, lock and unlock operations"""


def validate_user_task(user: str, task: str):
    """Function checking if user has rights to execute the task
    Rquired for: run"""


def display_available(user: str, *args):
    """Fucntion for displaying resources available to an entity"""


def lock_workdir():
    """Function locking working directory"""


def unlock_workdir():
    """Function unlocking working directory"""


def lock_inventory():
    """Function locking the inevntory for run execution"""


def unlock_inventory():
    """Function locking the inevntory for run execution"""


def call_prehooks():
    """Function for running prerequisite operations"""


def run_ansible_task():
    """Function for running core operation run - ansible-playbook"""


def call_posthooks():
    """Function for running postrequisite operations"""


def main():
    """ansible-deploy endpoint function"""

    start_ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    global logger
    log_dir = os.getcwd()
    logger = set_logging(log_dir, LOGNAME, start_ts)
    if len(sys.argv) < 2:
        logger.error("To fee arguments")
        sys.exit(2)

    subcommand = get_sub_command(sys.argv[1])
    options = parse_options(sys.argv[2:])
    validate_options(options, subcommand)
    #create_workdir(start_ts, WORKDIR)
    sys.exit(0)
