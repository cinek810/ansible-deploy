"""
Ansible callback plugin that logs to existing play_item_tasks table in initiated sqlite database.
Created and tailored for ansible-deployer project.
"""
# -*- coding: utf-8 -*-
# Copyright (c) 2012, Michael DeHaan, <michael.dehaan@gmail.com>
# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or
# https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# pylint: disable=duplicate-code

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import sqlite3
import time

from ansible.module_utils.common._collections_compat import MutableMapping
from ansible.plugins.callback import CallbackBase


# NOTE: in Ansible 1.2 or later general logging is available without
# this plugin, just set ANSIBLE_LOG_PATH as an environment variable
# or log_path in the DEFAULTS section of your ansible configuration
# file.  This callback is an example of per hosts logging for those
# that want it.


class CallbackModule(CallbackBase):
    """
    logs playbook results to sqlite db
    """
    CALLBACK_VERSION = 1.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'sqlite_deployer'
    CALLBACK_NEEDS_WHITELIST = True

    TABLE_NAME = "play_item_tasks"
    TABLE_COLUMNS = [
        "sequence_id",
        "timestamp",
        "result",
        "changed",
        "hostname",
        "task_name"
    ]
    TIME_FORMAT = "%b %d %Y %H:%M:%S"

    def __init__(self):

        super().__init__()
        self.db_dir = os.environ["SQLITE_PATH"]
        self.sequence = os.environ["SEQUENCE_ID"]
        self.connector = self.db_connect()
        self.cursor = self.connector.cursor()

    def set_options(self, task_keys=None, var_options=None, direct=None):
        super().set_options(task_keys=task_keys, var_options=var_options, direct=direct)

    def db_connect(self):
        """Create sqlite db connector"""
        return sqlite3.connect(self.db_dir)

    def log(self, result, category):
        """Log message to sqlite database"""
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

        try:
            self.cursor.execute(
                "INSERT INTO {} ({}, {}, {}, {}, {}, {}) VALUES(?,?,?,?,?,?);".format(
                self.TABLE_NAME, *self.TABLE_COLUMNS), (
                    self.sequence,
                    now,
                    category,
                    changed_status,
                    result._host.get_name(),
                    result._task.name
                )
            )
            self.connector.commit()
        except Exception as exc:
            print(exc)

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
