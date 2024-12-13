"""Module for running system processes"""

import os
import sys
import subprocess
from logging import Logger

from ansible_deployer.modules.globalvars import ANSIBLE_DEFAULT_CALLBACK_PLUGIN_PATH,\
    REQUIRED_CALLBACK_PLUGINS
from ansible_deployer.modules.outputs import blocks
from ansible_deployer.modules.outputs.formatting import Formatters
from ansible_deployer.modules.outputs.loggers import RunLogger

class Runners:
    """Class handling ansible hooks and ansible plays execution"""

    def __init__(self, logger, lock_obj, workdir, start_ts_raw, setup_hooks, log_path, db_path):
        self.logger = logger
        self.lock_obj = lock_obj
        self.workdir = workdir
        self.start_ts_raw = start_ts_raw
        self.setup_hooks = setup_hooks
        self.sequence_id = os.path.basename(self.workdir)
        self.log_path = log_path
        self.db_path = db_path

    @staticmethod
    def reassign_commit_and_workdir(commit: str, workdir: str):
        """Change workdir if commit is a path (option --self-setup enabled in main)"""
        if not commit:
            commit = ""
        elif os.path.exists(os.path.abspath(commit)):
            workdir = commit
            commit = ""

        return workdir, commit

    def setup_ansible(self, commit: str, conf_dir: str):
        """
        Function responsible for execution of setup_hooks
        It passes the "commit" to the hook if one given, if not the hook should
        checkout the default repo.
        """
        failed = False
        workdir, commit = Runners.reassign_commit_and_workdir(commit, self.workdir)

        for hook in self.setup_hooks:
            if hook["module"] == "script":
                try:
                    with subprocess.Popen([os.path.join(conf_dir, hook["opts"]["file"]), commit],
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                          stdin=subprocess.PIPE, cwd=workdir) as proc:
                        std_out, std_err = proc.communicate()
                        if proc.returncode != 0:
                            failed = True
                except Exception as e:
                    self.logger.critical("Failed executing %s: %s", hook["opts"]["file"], e)
                    sys.exit(41)
                else:
                    if std_out:
                        self.logger.info("Setup hook %s stdout:", hook["name"])
                        for line in std_out.split(b"\n"):
                            if line:
                                self.logger.info(line.decode("utf-8"))
                    if std_err:
                        self.logger.error("Setup hook %s stderr:", hook["name"])
                        for line in std_err.split(b"\n"):
                            if line:
                                self.logger.error(line.decode("utf-8"))
                    if proc.returncode:
                        self.logger.critical("Setup hook %s failed, cannot continue", hook["name"])
                        sys.exit(40)
                    else:
                        self.logger.info("Setup completed in %s", workdir)

            else:
                self.logger.error("Not supported")
            if failed:
                self.logger.critical("Program will exit now.")
                sys.exit(69)

    def get_playitems(self, config: dict, options: dict):
        """
        Function obtaining play items for specified task.
        :param config:
        :param task_name:
        :return:
        """
        playitems = []

        for item in config["tasks"]["tasks"]:
            if item["name"] == options["task"]:
                if options["subcommand"] == "run":
                    play_names = item["play_items"]
                elif options["subcommand"] == "verify":
                    play_names = item["verify_items"]
                else:
                    self.logger.critical("Should have never happen. Uncleaned lock left")
                    sys.exit(130)


        # Task existence in config file is validated earlier in
        # Validators.validate_option_values_against_config() so play_names will always be defined
        # pylint: disable=possibly-used-before-assignment
        for play in play_names:
            for item in config["tasks"]["play_items"]:
                if item["name"] == play:
                    skip = item.get("skip", [])
                    if skip:
                        for elem in item["skip"]:
                            if elem["infra"] == options["infra"] and \
                                elem["stage"] == options["stage"]:
                                self.logger.info("Skipping playitem %s on %s and %s stage.", play,
                                            options["infra"], options["stage"])
                                break
                        else:
                            playitems.append(item)
                    else:
                        playitems.append(item)

        # TODO add check if everything was skipped
        return playitems

    def run_playitem(self, callback_settings: dict, config: dict, options: dict, inventory: str,
                     lockpath: str, db_writer):
        """
        Function implementing actual execution of runner [ansible-playbook or py.test]
        """
        playitems = self.get_playitems(config, options)
        host_list = []
        returned = []
        if not playitems:
            self.logger.critical("No playitems found for requested task %s. Nothing to do.",
                                 options['task'])
            self.lock_obj.unlock_inventory(lockpath)
            sequence_records = db_writer.start_sequence_dict([""], self.setup_hooks, options,
                                                             self.start_ts_raw, self.sequence_id)
            db_writer.finalize_db_write(sequence_records, False)
            sys.exit(70)
        else:
            for playitem in playitems:
                run_logger = self.set_runner_logging(
                    options, playitem["name"], os.path.basename(inventory))
                command = self.construct_command(playitem, inventory, config, options)
                command_env = self.construct_env(options, callback_settings)
                self.logger.debug("Running '%s'.", command)
                try:
                    with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                          env=command_env) as proc:

                        for msg in proc.stdout:
                            dec_msg = msg.split(b"\n")[0].decode("utf-8")
                            returned.append(dec_msg)
                            run_logger.info(dec_msg)

                        proc.communicate()
                        format_obj = Formatters(self.logger)
                        parsed_std = format_obj.format_ansible_output(returned)
                        host_list = db_writer.parse_yaml_output_for_hosts(parsed_std["complete"],
                                                                self.sequence_id)
                        sequence_records = db_writer.start_sequence_dict(host_list,
                                                                         self.setup_hooks, options,
                                                                         self.start_ts_raw,
                                                                         self.sequence_id)

                        if proc.returncode == 0:
                            format_obj.positive_ansible_output(parsed_std["warning"],
                                                               parsed_std["output"], command)
                        else:
                            format_obj.negative_ansible_output(parsed_std["warning"],
                                                               parsed_std["error"], command)
                            self.lock_obj.unlock_inventory(lockpath)
                            db_writer.finalize_db_write(sequence_records, False)
                            blocks.log_exit_messages(
                                self.logger, self.workdir, self.log_path, self.db_path)
                            self.logger.critical("Program will exit now.")
                            sys.exit(71)
                except Exception as exc:
                    self.logger.critical("\"%s\" failed due to:")
                    self.logger.critical(exc)
                    sequence_records = db_writer.start_sequence_dict(host_list, self.setup_hooks,
                                                                     options, self.start_ts_raw,
                                                                     self.sequence_id)
                    db_writer.finalize_db_write(sequence_records, True)
                    sys.exit(72)
            return sequence_records

    @staticmethod
    def get_tags_for_task(config: dict, options: dict):
        """Function to get task's tags"""
        tags = []
        skip_tags = []
        for task in config["tasks"]["tasks"]:
            if task["name"] == options["task"]:
                tags = task.get("tags", [])

        if options["dry_mode"]:
            tags.append("ansible_deployer_dry_mode")

        for task in config["tasks"]["tasks"]:
            if task["name"] == options["task"]:
                skip_tags = task.get("skip_tags", [])

        return tags, skip_tags

    def construct_command(self, playitem: str, inventory: str, config: dict, options: dict):
        """Create final ansible command from available variables"""
        tags, skip_tags = Runners.get_tags_for_task(config, options)

        if "runner" in playitem and playitem["runner"] == "py.test":
            command = ["py.test", "--ansible-inventory", inventory]
            if options["limit"]:
                command.append(f"--hosts=ansible://{options['limit']}")
            else:
                command.append("--hosts=ansible://all")
            command.append("--junit-xml=junit_"+options['task']+'.xml')
            command.append("./"+playitem["file"])
        else:
            command = ["ansible-playbook", "-i", inventory, playitem["file"]]
            if options["limit"]:
                command.append("-l")
                command.append(options["limit"])
            if tags:
                command.append("-t")
                command.append(",".join(tags))
            if skip_tags:
                command.append("--skip-tags")
                command.append(",".join(skip_tags))
            if options["check_mode"]:
                command.append("-C")

        if options["runner_verb"]:
            command.append(f'-{"v"*options["runner_verb"]}')

        if options["runner_opts"]:
            for opt in options["runner_opts"].strip("'\"").split():
                command.append(opt)

        return command

    def construct_env(self, options: dict, callback_settings: dict) -> dict:
        """Create final ansible environment from available variables"""
        ansible_callbacks = list(set(options["runner_plugins"] + REQUIRED_CALLBACK_PLUGINS))
        ansible_stdout_callback = options["runner_stdout"] if options["runner_stdout"]\
            else callback_settings["def_stdout_plugin"]
        return dict(
            os.environ, ANSIBLE_CALLBACKS_ENABLED=",".join(ansible_callbacks),
            ANSIBLE_CALLBACK_PLUGINS=self.append_to_ansible_callbacks_path(),
            ANSIBLE_LOAD_CALLBACK_PLUGINS="1", ANSIBLE_NOCOWS="1", LOG_PLAYS_PATH=self.log_path,
            ANSIBLE_STDOUT_CALLBACK=ansible_stdout_callback, SQLITE_PATH=self.db_path,
            SEQUENCE_ID=self.sequence_id
        )

    @staticmethod
    def append_to_ansible_callbacks_path():
        """Create final searchable path for ansible callback plugins"""
        plugin_path = os.path.join(os.path.realpath(__file__).rsplit(os.sep, 3)[0], "plugins")
        return f'{ANSIBLE_DEFAULT_CALLBACK_PLUGIN_PATH}:{plugin_path}'

    def set_runner_logging(self, options: dict, playitem: str, inventory: str) -> Logger:
        """Return logger with handlers instantiated from RunLoggers"""
        logger = RunLogger(options, self.workdir, playitem, inventory)
        logger.add_raw_handlers(self.log_path)

        return logger.logger
