"""Main module for ansible-deploy"""

import sys
import os
import argparse
import logging
import datetime
#TODO: Add an option to explicitly enable syslog logging
#from logging import handlers as log_han

import yaml
from cerberus import Validator


LOGNAME = "ansible-deploy_execution_{}.log"
SEQUENCE_PREFIX = "SEQ"
PARENT_WORKDIR = "/tmp"
CONF_DIR = "/etc/ansible-deploy/"


def get_sub_command(command):
    """Function to check the first arguments (argv[1..]) looking for a subcommand"""
    if command == "run":
        subcommand = "run"
    elif command == "lock":
        subcommand = "lock"
    elif command == "unlock":
        subcommand = "unlock"
    elif command == "list":
        subcommand = "list"
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
    options["infra"] = arguments.infrastructure[0]
    options["stage"] = arguments.stage[0]
    options["commit"] = arguments.commit[0]
    options["task"] = arguments.task[0]

    return options

def create_workdir(timestamp: str, base_dir: str):
    """
    Function to create working directory on file system, we expect it to change
    the cwd to newly created workdir at the end.
    """
    logger.debug("Entering create_workdir")
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

    #TODO: Add error handling
    os.makedirs(seq_path)
    os.chdir(seq_path)
    logger.info("Successfully created workdir: %s", seq_path)
    return seq_path

def validate_options(options, subcommand):
    """Function checking if the options set are allowed in this subcommand"""
    logger.debug("validate_options running for subcommand: %s", (subcommand))
    required = []
    notsupported = []
    if subcommand == "run":
        required = ["task", "infra", "stage"]
    elif subcommand in ("lock", "unlock"):
        required = ["infra", "stage"]
        notsupported = ["task", "commit"]
    elif subcommand == "list":
        notsupported = ["commit"]

    failed = False
    for req in required:
        if options[req] is None:
            logger.error("%s is required for %s", req, subcommand)
            failed = True

    for notsup in notsupported:
        if options[notsup] is not None:
            logger.error("%s is not supported by %s", notsup, subcommand)
            failed = True

    if failed:
        logger.error("Failed to validate options")
        sys.exit(55)

def load_configuration_file(config_file):
    """Function responsible for single file loading and validation"""
    #TODO: Add verification of owner/group/persmissions
    logger.debug("Loading :%s", config_file)

    with open(os.path.join(CONF_DIR, config_file), "r", encoding="utf8") as config_stream:
        try:
            config = yaml.safe_load(config_stream)
        except yaml.YAMLError as e:
            logger.error(e)
            sys.exit(51)

    with open(os.path.join(CONF_DIR, "schema", config_file), "r", encoding="utf8") as schema_stream:
        try:
            schema = yaml.safe_load(schema_stream)
        except yaml.YAMLError as e:
            logger.error(e)
            sys.exit(52)
    validator = Validator(schema)
    if not validator.validate(config, schema):
        logger.error(validator.errors)
        sys.exit(53)
    logger.debug("Loaded:\n%s", str(config))
    return config

def load_configuration():
    """Function responsible for reading configuration files and running a schema validator against
    it
    """
    logger.debug("load_configuration called")
    #TODO: validate files/directories permissions - should be own end editable only by special user

    infra = load_configuration_file("infra.yaml")
    tasks = load_configuration_file("tasks.yaml")

    config = {}
    config["infra"] = infra["infrastructures"]
    config["tasks"] = tasks

    return config

def validate_option_by_dict_with_name(optval, conf_dict):
    """
    Validate if given dictionary contains element with name equal to optval
    """
    if optval:
        for elem in conf_dict:
            if elem["name"] == optval:
                break
        else:
            logger.error("%s not found in configuration file.", optval)
            sys.exit(54)

def validate_user_infra_stage():
    """Function checking if user has rights to execute command on selected infrastructure
    Required for: run, lock and unlock operations"""

def validate_user_task():
    """Function checking if user has rights to execute the task
    Rquired for: run"""

def validate_option_values_with_config(config, options):
    """
    Function responsible for checking if option values match configuration
    """
    validate_option_by_dict_with_name(options["infra"], config["infra"])
    validate_option_by_dict_with_name(options["task"], config["tasks"]["tasks"])
    #TODO: validate if user is allowed to use --commit
    #TODO: validate if user is allowed to execute the task on infra/stag pair
    #(validate_user_infra_stage(), validate_usr_task())


def lock_inventory(infra, stage):
    """
    Function responsible for locking inventory file.
    The goal is to prevent two parallel ansible-deploy's running on the same inventory
    This needs to be done by the use of additional directory under PARNT_WORKDIR,, for instance:
    PARENT_WORKDIR/locks.
    We shouldn't check if file exists, but rather attempt to open it for writing, until we're
    done every other process should be rejected this access.
    The file should match inventory file name.
    """

def unlock_inventory(infra, stage):
    """
    Function responsible for unlocking inventory file, See also lock_inventory
    """
def setup_ansible(config, commit):
    """
    Function responsible for execution of setup_hooks
    It passes the "commit" to the hook if one given, if not the hook should
    checkout the default repo.
    """
def run_task(config, options):
    """
    Function implementing actual execution of ansible-playbook
    """

def list_tasks(config, options):
    """
    Function listing tasks available to the user limited to given infra/stage/task
    """

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
    config = load_configuration()
    validate_option_values_with_config(config, options)

    if subcommand == "run":
        create_workdir(start_ts, PARENT_WORKDIR)
        setup_ansible(config["tasks"]["setup_hooks"], options["commit"])
        lock_inventory(options["infra"], options["stage"])
        run_task(config, options)
        unlock_inventory(options["infra"], options["stage"])
    elif subcommand == "lock":
        lock_inventory(options["infra"], options["stage"])
    elif subcommand == "unlock":
        unlock_inventory(options["infra"], options["stage"])
    elif subcommand == "list":
        list_tasks(config, options)

    sys.exit(0)
