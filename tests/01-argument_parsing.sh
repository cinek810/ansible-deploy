#!/bin/bash -l


source ./tests/testing_lib.sh

echo -e "   ___  _                                                      _                          _\n  / _ \/ |           __ _ _ __ __ _ _   _ _ __ ___   ___ _ __ | |_   _ __   __ _ _ __ ___(_)_ __   __ _\n | | | | |  _____   / _\` | '__/ _\` | | | | '_ \` _ \ / _ \ '_ \| __| | '_ \ / _\` | '__/ __| | '_ \ / _\` |\n | |_| | | |_____| | (_| | | | (_| | |_| | | | | | |  __/ | | | |_  | |_) | (_| | |  \__ \ | | | | (_| |\n  \___/|_|          \__,_|_|  \__, |\__,_|_| |_| |_|\___|_| |_|\__| | .__/ \__,_|_|  |___/_|_| |_|\__, |\n                              |___/                                 |_|                           |___/\n                                                       _     _             _   _\n __      ___ __ ___  _ __   __ _    ___ ___  _ __ ___ | |__ (_)_ __   __ _| |_(_) ___  _ __  ___\n \ \ /\ / / '__/ _ \| '_ \ / _\` |  / __/ _ \| '_ \` _ \| '_ \| | '_ \ / _\` | __| |/ _ \| '_ \/ __|\n  \ V  V /| | | (_) | | | | (_| | | (_| (_) | | | | | | |_) | | | | | (_| | |_| | (_) | | | \__ \ \n   \_/\_/ |_|  \___/|_| |_|\__, |  \___\___/|_| |_| |_|_.__/|_|_| |_|\__,_|\__|_|\___/|_| |_|___/\n                           |___/\n"
# Check wrong combinations
check_message_in_output "ansible-deployer" "\[CRITICAL\]: Too few arguments"
check_message_in_output "ansible-deployer run" "\[ERROR\]: Option --task is required for run"
check_message_in_output "ansible-deployer verify" "\[ERROR\]: Option --task is required for verify"
check_message_in_output "ansible-deployer run" "\[ERROR\]: Option --infrastructure is required for run"
check_message_in_output "ansible-deployer verify" "\[ERROR\]: Option --infrastructure is required for verify"
check_message_in_output "ansible-deployer run" "\[ERROR\]: Option --stage is required for run"
check_message_in_output "ansible-deployer verify" "\[ERROR\]: Option --stage is required for verify"
check_message_in_output "ansible-deployer run --task task_exec_bin_true" "\[ERROR\]: Option --stage is required for run"
check_message_in_output "ansible-deployer verify --task task_exec_bin_true" "\[ERROR\]: Option --stage is required for verify"
check_message_in_output "ansible-deployer run --task task_exec_bin_true" "\[ERROR\]: Option --infrastructure is required for run"
check_message_in_output "ansible-deployer verify --task task_exec_bin_true" "\[ERROR\]: Option --infrastructure is required for verify"
check_message_in_output "ansible-deployer run --task task_exec_bin_true --infrastructure testInfra" "Option --stage is required for run"
check_message_in_output "ansible-deployer verify --task task_exec_bin_true --infrastructure testInfra" "Option --stage is required for verify"

check_message_in_output "ansible-deployer --task task_exec_bin_true --infrastructure testInfra" "\[CRITICAL\]: First positional argument (subcommand) is required! Available commands are: run, lock, unlock, verify, show."

check_message_in_output "ansible-deployer verify --task task_exec_bin_true --infrastructure testInfra --stage prod --commit testCommit" "Option --commit is not supported by verify"
check_message_in_output "ansible-deployer lock --task task_exec_bin_true --infrastructure testInfra" "\[ERROR\]: Option --task is not supported by lock"
check_message_in_output "ansible-deployer lock --task task_exec_bin_true --infrastructure testInfra --stage prod" "\[ERROR\]: Option --task is not supported by lock"
check_message_in_output "ansible-deployer lock --task task_exec_bin_true --stage prod" "\[ERROR\]: Option --infrastructure is required for lock"
check_message_in_output "ansible-deployer lock --task task_exec_bin_true --stage prod --commit X" "\[ERROR\]: Option --commit is not supported by lock"
check_message_in_output "ansible-deployer lock --infra testInfra --stage prod --keep-locked" "\[ERROR\]: Option --keep-locked is not supported by lock"
check_message_in_output "ansible-deployer lock --task task_exec_bin_true --limit test_hosts_1" "\[ERROR\]: Option --limit is not supported by lock"
check_message_in_output "ansible-deployer lock --infra testInfra --stage prod --raw-runner-output" "\[ERROR\]: Option --raw-runner-output is not supported by lock"
check_message_in_output "ansible-deployer lock --infra testInfra --stage prod --self-setup ." "\[ERROR\]: Option --self-setup is not supported by lock"

check_message_in_output "ansible-deployer unlock --task task_exec_bin_true --infrastructure testInfra" "\[ERROR\]: Option --task is not supported by unlock"
check_message_in_output "ansible-deployer unlock --task task_exec_bin_true --infrastructure testInfra --stage prod" "\[ERROR\]: Option --task is not supported by unlock"
check_message_in_output "ansible-deployer unlock --task task_exec_bin_true --stage test" "\[ERROR\]: Option --infrastructure is required for unlock"
check_message_in_output "ansible-deployer unlock --task task_exec_bin_true --stage prod --commit X" "\[ERROR\]: Option --commit is not supported by unlock"
check_message_in_output "ansible-deployer unlock --infra testInfra --stage prod --keep-locked" "\[ERROR\]: Option --keep-locked is not supported by unlock"
check_message_in_output "ansible-deployer unlock --task task_exec_bin_true --limit test_hosts_1" "\[ERROR\]: Option --limit is not supported by unlock"
check_message_in_output "ansible-deployer unlock --infra testInfra --stage prod --raw-runner-output" "\[ERROR\]: Option --raw-runner-output is not supported by unlock"
check_message_in_output "ansible-deployer unlock --infra testInfra --stage prod --self-setup ." "\[ERROR\]: Option --self-setup is not supported by unlock"

check_message_in_output "ansible-deployer run test" "\[CRITICAL\]: Too many positional arguments! Only subcommand \"show\" can accept following arguments: all, task, infra."
check_message_in_output "ansible-deployer verify test" "\[CRITICAL\]: Too many positional arguments! Only subcommand \"show\" can accept following arguments: all, task, infra."
check_message_in_output "ansible-deployer lock test" "\[CRITICAL\]: Too many positional arguments! Only subcommand \"show\" can accept following arguments: all, task, infra."
check_message_in_output "ansible-deployer unlock test" "\[CRITICAL\]: Too many positional arguments! Only subcommand \"show\" can accept following arguments: all, task, infra."
check_message_in_output "ansible-deployer show test" "\[CRITICAL\]: Invalid argument test! Subcommand \"show\" can accept only following arguments: all, task, infra."
check_message_in_output "ansible-deployer show --commit task_exec_bin_true" "\[ERROR\]: Option --commit is not supported by show"
check_message_in_output "ansible-deployer show --limit test_hosts_1" "\[ERROR\]: Option --limit is not supported by show"
check_message_in_output "ansible-deployer show --task task_exec_bin_true" "\[ERROR\]: Option --task is not supported by show"
check_message_in_output "ansible-deployer show --infra testInfra" "\[ERROR\]: Option --infrastructure is not supported by show"
check_message_in_output "ansible-deployer show --stage prod" "\[ERROR\]: Option --stage is not supported by show"
check_message_in_output "ansible-deployer show --dry" "\[ERROR\]: Option --dry is not supported by show"
check_message_in_output "ansible-deployer show --keep-locked" "\[ERROR\]: Option --keep-locked is not supported by show"
check_message_in_output "ansible-deployer show --syslog" "\[ERROR\]: Option --syslog is not supported by show"
check_message_in_output "ansible-deployer show --raw-runner-output" "\[ERROR\]: Option --raw-runner-output is not supported by show"
check_message_in_output "ansible-deployer show --self-setup ." "\[ERROR\]: Option --self-setup is not supported by show"

echo -e "   ___  _                                                      _                          _\n  / _ \/ |           __ _ _ __ __ _ _   _ _ __ ___   ___ _ __ | |_   _ __   __ _ _ __ ___(_)_ __   __ _\n | | | | |  _____   / _\` | '__/ _\` | | | | '_ \` _ \ / _ \ '_ \| __| | '_ \ / _\` | '__/ __| | '_ \ / _\` |\n | |_| | | |_____| | (_| | | | (_| | |_| | | | | | |  __/ | | | |_  | |_) | (_| | |  \__ \ | | | | (_| |\n  \___/|_|          \__,_|_|  \__, |\__,_|_| |_| |_|\___|_| |_|\__| | .__/ \__,_|_|  |___/_|_| |_|\__, |\n                              |___/                                 |_|                           |___/\n                               _                         _     _             _   _\n   ___ ___  _ __ _ __ ___  ___| |_    ___ ___  _ __ ___ | |__ (_)_ __   __ _| |_(_) ___  _ __  ___\n  / __/ _ \| '__| '__/ _ \/ __| __|  / __/ _ \| '_ \` _ \| '_ \| | '_ \ / _\` | __| |/ _ \| '_ \/ __|\n | (_| (_) | |  | | |  __/ (__| |_  | (_| (_) | | | | | | |_) | | | | | (_| | |_| | (_) | | | \__ \ \n  \___\___/|_|  |_|  \___|\___|\__|  \___\___/|_| |_| |_|_.__/|_|_| |_|\__,_|\__|_|\___/|_| |_|___/\n"
# Check if correct combinations are accepted
check_run_ok "ansible-deployer run --dry --task task_exec_bin_true --stage prod --infrastructure testInfra"
check_run_ok "ansible-deployer verify --dry --task task_exec_bin_true --stage prod --infrastructure testInfra"
check_run_ok "ansible-deployer run --dry --task task_with_limit --stage testing --infrastructure testInfra --limit testHost1"
check_run_ok "ansible-deployer verify --dry --task task_with_limit --stage testing --infrastructure testInfra --limit testHost1"
check_run_ok "ansible-deployer run --dry --task task_exec_bin_true --stage prod --infrastructure testInfra --commit test_version"
check_run_ok "ansible-deployer lock --dry --stage prod --infrastructure testInfra"
check_run_ok "ansible-deployer unlock --dry --stage prod --infrastructure testInfra"
check_run_ok "ansible-deployer show"
check_run_ok "ansible-deployer show infra"

echo -e "   ___  _                                                      _                          _\n  / _ \/ |           __ _ _ __ __ _ _   _ _ __ ___   ___ _ __ | |_   _ __   __ _ _ __ ___(_)_ __   __ _\n | | | | |  _____   / _\` | '__/ _\` | | | | '_ \` _ \ / _ \ '_ \| __| | '_ \ / _\` | '__/ __| | '_ \ / _\` |\n | |_| | | |_____| | (_| | | | (_| | |_| | | | | | |  __/ | | | |_  | |_) | (_| | |  \__ \ | | | | (_| |\n  \___/|_|          \__,_|_|  \__, |\__,_|_| |_| |_|\___|_| |_|\__| | .__/ \__,_|_|  |___/_|_| |_|\__, |\n                              |___/                                 |_|                           |___/\n                                                    __ _\n __      ___ __ ___  _ __   __ _    ___ ___  _ __  / _(_) __ _\n \ \ /\ / / '__/ _ \| '_ \ / _\` |  / __/ _ \| '_ \| |_| |/ _\` |\n  \ V  V /| | | (_) | | | | (_| | | (_| (_) | | | |  _| | (_| |\n   \_/\_/ |_|  \___/|_| |_|\__, |  \___\___/|_| |_|_| |_|\__, |\n                           |___/                         |___/\n"
# Check if wrong config is rejected
check_message_in_output "ansible-deployer run --dry --task task_exec_bin_true --infrastructure nonExistingInfra --stage prod" "\[CRITICAL\]: nonExistingInfra not found in configuration file"
