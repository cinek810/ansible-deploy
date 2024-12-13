"""Main module for ansible-deploy"""

import os
import sys
import datetime
import errno
from ansible_deployer.modules.configs.config import Config
from ansible_deployer.modules.locking.locking import Locking
from ansible_deployer.modules.misc import utils as mutils
from ansible_deployer.modules.misc.arguments import CliInput
from ansible_deployer.modules.outputs import blocks
from ansible_deployer.modules.outputs.loggers import AppLogger
from ansible_deployer.modules.validators.validate import Validators
from ansible_deployer.modules.runners.run import Runners
from ansible_deployer.modules.database.creator import DbSetup
from ansible_deployer.modules.database.writer import DbWriter
from ansible_deployer.modules import globalvars


def main(options: dict):
    """ansible-deployer main function"""
    start_ts_raw = datetime.datetime.now()
    start_ts = start_ts_raw.strftime("%Y%m%d_%H%M%S")

    if len(sys.argv) < 2:
        print(f"{globalvars.PRINT_FAIL}[CRITICAL]: Too few arguments{globalvars.PRINT_END}",
              file=sys.stderr)
        sys.exit(2)

    logger = AppLogger(options)

    configuration = Config(logger.logger, options["conf_dir"])
    config = configuration.load_configuration()

    if options["subcommand"] in ("run", "verify"):
        workdir = mutils.create_workdirs(start_ts, configuration.conf, logger.logger)
        log_path = os.path.join(
            workdir, configuration.conf["file_naming"]["log_file_name_frmt"].format(start_ts))
        logger.add_file_handler(log_path, logger.basic_formatter)
        logger.flush_memory_handler(True, options["syslog"])
    else:
        logger.flush_memory_handler(False, options["syslog"])

    validators = Validators(logger.logger)
    validators.validate_options(options)
    selected_items = validators.validate_option_values_against_config(config, options)

    if options["subcommand"] in ("run", "verify"):
        os.chdir(options["self_setup"] if options["self_setup"] else workdir)

    user_groups = mutils.get_all_user_groups(logger.logger)

    if options["conf_val"]:
        logger.logger.info("Validation of configuration files was successful, program will exit now"
                           ".")
        sys.exit(0)

    if options["subcommand"] == "show":
        mutils.show_deployer(config, options)
    else:
        inv_file = mutils.get_inventory_file(config, options, logger.logger)

        lockpath = os.path.join(os.path.join(configuration.conf["global_paths"]["work_dir"],
                                "locks") , inv_file.lstrip(f".{os.sep}").replace(os.sep, "_"))
        lock = Locking(logger.logger, options["keep_locked"], (options["infra"], options["stage"]),
                       configuration.conf)
        if options["subcommand"] in ("run", "verify"):
            if not validators.verify_task_permissions(selected_items, user_groups, config):
                logger.logger.critical("Task forbidden")
                sys.exit(errno.EPERM)
            db_connector, db_path = DbSetup.connect_to_db(DbSetup(logger.logger, start_ts,
                                                          configuration.conf, options))
            db_writer = DbWriter(logger.logger, db_connector, db_path)
            runner = Runners(logger.logger, lock, workdir, start_ts_raw,
                             config["tasks"]["setup_hooks"], log_path, db_path)
            if not options["self_setup"]:
                runner.setup_ansible(selected_items["commit"], configuration.conf_dir)
            if options["lock"]:
                lock.lock_inventory(lockpath)
            sequence_record_dict = runner.run_playitem(configuration.conf["callback_settings"],
                                                       config, options, inv_file, lockpath,
                                                       db_writer)
            if options["lock"]:
                lock.unlock_inventory(lockpath)
            blocks.log_exit_messages(logger.logger, workdir, log_path, db_path)
            db_writer.finalize_db_write(sequence_record_dict, False)
        elif options["subcommand"] == "lock":
            lock.lock_inventory(lockpath)
        elif options["subcommand"] == "unlock":
            lock.unlock_inventory(lockpath)

    sys.exit(0)


def ansible_deployer():
    """ansible-deployer endpoint function"""
    return main(CliInput.parse_arguments(CliInput()))


if __name__ == "__main__":
    ansible_deployer()
