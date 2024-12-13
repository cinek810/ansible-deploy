"""Ansible callback plugin that logs to a file, based on community.general.log_plays 2.0"""
# -*- coding: utf-8 -*-

# pylint: disable=duplicate-code

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import time

from ansible.utils.path import makedirs_safe
from ansible.module_utils.common.text.converters import to_bytes
from ansible.module_utils.common._collections_compat import MutableMapping
from ansible.plugins.callback import CallbackBase


class CallbackModule(CallbackBase):
    """
    logs playbook results in defined logfile
    """
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'log_plays_adjusted'
    CALLBACK_NEEDS_WHITELIST = True

    TIME_FORMAT = "%b %d %Y %H:%M:%S"
    MSG_FORMAT = "%(now)s - %(hostname)s - %(playbook)s - %(task_name)s - %(category)s - changed:"\
            " %(changed_status)s\n\n"

    def __init__(self):

        super().__init__()
        self.log_path = os.environ["LOG_PLAYS_PATH"]

    def set_options(self, task_keys=None, var_options=None, direct=None):
        """Set ansible options and try to create log directory"""
        super().set_options(task_keys=task_keys, var_options=var_options, direct=direct)

        log_dir = os.path.dirname(self.log_path)
        if not os.path.exists(log_dir):
            makedirs_safe(log_dir)

    def log(self, result, category):
        """Log message to log file"""
        data = result._result
        if isinstance(data, MutableMapping):
            if '_ansible_verbose_override' in data:
                # avoid logging extraneous data
                data = 'omitted'

        try:
            changed_status = str(data.get("changed", "Unknown"))
        except AttributeError:
            changed_status = "Unknown"

        now = time.strftime(self.TIME_FORMAT, time.localtime())

        msg = to_bytes(
            self.MSG_FORMAT
            % {
                "now": now,
                "hostname": result._host.get_name(),
                "playbook": self.playbook,
                "task_name": result._task.name,
                "category": category,
                "changed_status": changed_status
            }
        )
        with open(self.log_path, "ab") as fd:
            fd.write(msg)

    def v2_runner_on_failed(self, result, ignore_errors=False):
        """Log result when runner failed"""
        self.log(result, 'FAILED')

    def v2_runner_on_ok(self, result):
        """Log result when runner passed"""
        self.log(result, 'OK')

    def v2_runner_on_skipped(self, result):
        """Log result when runner skipped host"""
        self.log(result, 'SKIPPED')

    def v2_runner_on_unreachable(self, result):
        """Log result when host was unreachable"""
        self.log(result, 'UNREACHABLE')

    def v2_runner_on_async_failed(self, result):
        """Log result when async failed"""
        self.log(result, 'ASYNC_FAILED')

    def v2_playbook_on_start(self, playbook):
        """Log runner start"""
        # pylint: disable=attribute-defined-outside-init
        self.playbook = playbook._file_name

    def v2_playbook_on_import_for_host(self, result, imported_file):
        """Log runner import"""
        self.log(result, 'IMPORTED')

    def v2_playbook_on_not_import_for_host(self, result, missing_file):
        """Log runner not import"""
        self.log(result, 'NOTIMPORTED')
