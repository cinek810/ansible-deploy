#!/bin/bash -l


source ./tests/testing_lib.sh

echo -e "   ___ ____                      _               _\n  / _ \___ \ __ _            ___| |__   ___  ___| | ___ __ _   _ _ __\n | | | |__) / _\` |  _____   / __| '_ \ / _ \/ __| |/ / '__| | | | '_ \ \n | |_| / __/ (_| | |_____| | (__| | | |  __/ (__|   <| |  | |_| | | | |\n  \___/_____\__,_|          \___|_| |_|\___|\___|_|\_\_|   \__,_|_| |_|\n \n                               _\n   ___ ___  _ __ _ __ ___  ___| |_    _____  _____  ___\n  / __/ _ \| '__| '__/ _ \/ __| __|  / _ \ \/ / _ \/ __|\n | (_| (_) | |  | | |  __/ (__| |_  |  __/>  <  __/ (__\n  \___\___/|_|  |_|  \___|\___|\__|  \___/_/\_\___|\___|\n"
# Correct execution
check_run_ok "ansible-deployer run --task task_exec_bin_true --stage prod --infrastructure testInfra"
check_run_ok "ansible-deployer run --task task_with_limit --stage testing --infrastructure testInfra --limit testHost1"
check_run_ok "ansible-deployer run --task tagged_task_true --stage testing --infrastructure testInfra"
check_run_ok "ansible-deployer verify --task task_exec_bin_true --stage prod --infrastructure testInfra"
check_run_ok "ansible-deployer run --task skip_task_tagged_task_false --stage testing --infrastructure testInfra"
check_run_fail "ansible-deployer run --task tagged_task_false --stage testing --infrastructure testInfra"

echo -e "   ___ ____                      _               _\n  / _ \___ \ __ _            ___| |__   ___  ___| | ___ __ _   _ _ __\n | | | |__) / _\` |  _____   / __| '_ \ / _ \/ __| |/ / '__| | | | '_ \ \n | |_| / __/ (_| | |_____| | (__| | | |  __/ (__|   <| |  | |_| | | | |\n  \___/_____\__,_|          \___|_| |_|\___|\___|_|\_\_|   \__,_|_| |_|\n \n  _                 _ _     _               _   _\n (_)_ ____   ____ _| (_) __| |   ___  _ __ | |_(_) ___  _ __  ___\n | | '_ \ \ / / _\` | | |/ _\` |  / _ \| '_ \| __| |/ _ \| '_ \/ __|\n | | | | \ V / (_| | | | (_| | | (_) | |_) | |_| | (_) | | | \__ \ \n |_|_| |_|\_/ \__,_|_|_|\__,_|  \___/| .__/ \__|_|\___/|_| |_|___/\n                                     |_|\n"
# Non-existent option values
check_message_in_output "ansible-deployer run --task task_exec_bin_ERR --stage prod --infrastructure testInfra" "\[CRITICAL\]: task_exec_bin_ERR not found in configuration file."
check_message_in_output "ansible-deployer run --task task_exec_bin_true --stage prod --infrastructure testInfra_ERR" "\[CRITICAL\]: testInfra_ERR not found in configuration file."
check_message_in_output "ansible-deployer run --task task_exec_bin_true --stage prod_ERR --infrastructure testInfra" "\[CRITICAL\]: prod_ERR not found in configuration file."

echo -e "   ___ ____                      _               _\n  / _ \___ \ __ _            ___| |__   ___  ___| | ___ __ _   _ _ __\n | | | |__) / _\` |  _____   / __| '_ \ / _ \/ __| |/ / '__| | | | '_ \ \n | |_| / __/ (_| | |_____| | (__| | | |  __/ (__|   <| |  | |_| | | | |\n  \___/_____\__,_|          \___|_| |_|\___|\___|_|\_\_|   \__,_|_| |_|\n \n      _    _             _\n  ___| | _(_)_ __  _ __ (_)_ __   __ _\n / __| |/ / | '_ \| '_ \| | '_ \ / _\` |\n \__ \   <| | |_) | |_) | | | | | (_| |\n |___/_|\_\_| .__/| .__/|_|_| |_|\__, |\n            |_|   |_|            |___/\n"
# Check infra/stage skipping
## Sometimes skip (depending on stage)
check_message_in_output "ansible-deployer run --task task_skipping --stage testing --infrastructure testInfra" "\[INFO\]: Skipping playitem"
check_message_in_output "ansible-deployer run --task task_skipping --stage prod --infrastructure testInfra" "ran succesfully"
## Always skip
check_message_not_in_output "ansible-deployer run --task task_skipping --stage testing --infrastructure testInfra2" "ran succesfully"
## Never skip
check_message_not_in_output "ansible-deployer run --task task_skipping --stage prod --infrastructure testInfra3" "\[INFO\]: Skipping playitem"

echo -e "   ___ ____                      _               _\n  / _ \___ \ __ _            ___| |__   ___  ___| | ___ __ _   _ _ __\n | | | |__) / _\` |  _____   / __| '_ \ / _ \/ __| |/ / '__| | | | '_ \ \n | |_| / __/ (_| | |_____| | (__| | | |  __/ (__|   <| |  | |_| | | | |\n  \___/_____\__,_|          \___|_| |_|\___|\___|_|\_\_|   \__,_|_| |_|\n \n                                _ _\n   ___ ___  _ __ ___  _ __ ___ (_) |_ ___\n  / __/ _ \| '_ \` _ \| '_ \` _ \| | __/ __|\n | (_| (_) | | | | | | | | | | | | |_\__ \ \n  \___\___/|_| |_| |_|_| |_| |_|_|\__|___/\n"
# Check --commit option
check_run_ok "ansible-deployer run --task task_with_commit --stage testing --infrastructure testInfra --commit tags/v1.1"
check_run_ok "ansible-deployer run --task task_with_commit --stage testing --infrastructure testInfra --commit tags/v2.4"
check_run_ok "ansible-deployer run --task task_with_commit --stage testing --infrastructure testInfra --commit tags/v2.5.1"
check_run_ok "ansible-deployer run --task task_with_commit --stage testing --infrastructure testInfra --commit tags/v3.6.5"
check_message_in_output "ansible-deployer run --task task_with_commit --stage testing --infrastructure testInfra --commit tags/v1.0.1" "\[ERROR\]: Requested commit tags/v1.0.1 is not valid for task task_with_commit."
check_message_in_output "ansible-deployer run --task task_with_commit --stage testing --infrastructure testInfra --commit tags/v2.1" "\[ERROR\]: Requested commit tags/v2.1 is not valid for task task_with_commit."
check_message_in_output "ansible-deployer run --task task_with_commit --stage testing --infrastructure testInfra --commit tags/v3.6.6" "\[ERROR\]: Requested commit tags/v3.6.6 is not valid for task task_with_commit."
check_message_in_output "ansible-deployer verify --task task_exec_bin_true --stage prod --infrastructure testInfra --raw-runner-output" "1 passed"

echo -e "   ___ ____                      _               _\n  / _ \___ \ __ _            ___| |__   ___  ___| | ___ __ _   _ _ __\n | | | |__) / _\` |  _____   / __| '_ \ / _ \/ __| |/ / '__| | | | '_ \ \n | |_| / __/ (_| | |_____| | (__| | | |  __/ (__|   <| |  | |_| | | | |\n  \___/_____\__,_|          \___|_| |_|\___|\___|_|\_\_|   \__,_|_| |_|\n \n        _   _\n   ___ | |_| |__   ___ _ __ ___\n  / _ \| __| '_ \ / _ \ '__/ __|\n | (_) | |_| | | |  __/ |  \__ \ \n  \___/ \__|_| |_|\___|_|  |___/\n"
# Miscellaneous
check_message_in_output "ansible-deployer run --task task_empty --stage testing --infrastructure testInfra" "\[CRITICAL\]: No playitems found for requested task"
check_message_in_output "ansible-deployer run --task task_exec_bin_true --stage prod --infrastructure testInfra" "\[INFO\]: setup_work_dir finished succesfully"

# Check --conf-validation run
check_message_in_output "ansible-deployer run --conf-validation --debug --task task_exec_bin_true --stage prod --infrastructure testInfra" "\[INFO\]: Validation of configuration files was successful, program will exit now."
check_message_not_in_output "ansible-deployer run --conf-validation --debug --task task_exec_bin_true --stage prod --infrastructure testInfra" "\[DEBUG\]: Started lock_inventory for lockdir"

# Check --check-mode option
check_message_in_output "ansible-deployer run --check-mode --debug --task task_exec_bin_true --stage prod --infrastructure testInfra --raw-runner-output" "msg: Command would have run if not in check mode"

# Check --dry-mode option
check_message_in_output "ansible-deployer run --dry-mode --debug --task task_with_pretask --stage testing --infrastructure testInfra --raw-runner-output" "TASK \[Run dummy pre_task\]"
check_message_not_in_output "ansible-deployer run --dry-mode --debug --task task_with_pretask --stage testing --infrastructure testInfra --raw-runner-output" "TASK \[Run /bin/false\]"

# Artificially generate lock
check_run_ok "ansible-deployer lock --stage locked --infrastructure testInfra"
check_message_in_output "ansible-deployer run --task task_exec_bin_true --stage locked --infrastructure testInfra" "is using this infrastructure, please try again later."
check_run_ok "ansible-deployer unlock --stage locked --infrastructure testInfra"

echo -e "   ___ ____                      _               _\n  / _ \___ \ __ _            ___| |__   ___  ___| | ___ __ _   _ _ __\n | | | |__) / _\` |  _____   / __| '_ \ / _ \/ __| |/ / '__| | | | '_ \ \n | |_| / __/ (_| | |_____| | (__| | | |  __/ (__|   <| |  | |_| | | | |\n  \___/_____\__,_|          \___|_| |_|\___|\___|_|\_\_|   \__,_|_| |_|\n \n              _               _                         _ _  __ _\n   ___  _   _| |_ _ __  _   _| |_   _ __ ___   ___   __| (_)/ _(_) ___ _ __ ___\n  / _ \| | | | __| '_ \| | | | __| | '_ \` _ \ / _ \ / _\` | | |_| |/ _ \ '__/ __|\n | (_) | |_| | |_| |_) | |_| | |_  | | | | | | (_) | (_| | |  _| |  __/ |  \__ \ \n  \___/ \__,_|\__| .__/ \__,_|\__| |_| |_| |_|\___/ \__,_|_|_| |_|\___|_|  |___/\n                 |_|\n"
# Check --debug option
check_run_ok "ansible-deployer show --debug" "\[DEBUG\]: load_configuration called"

# Check different output options
check_message_with_newline_in_output "ansible-deployer run --task task_with_ansible_fail --stage testing --infrastructure testInfra" "\[ERROR\]:.*\n\n\nTASK \[Run ll\]"
check_message_with_newline_in_output "ansible-deployer run --task task_with_ansible_fail --stage testing --infrastructure testInfra --raw-runner-output" "\[ERROR\]:.*\n\n\nTASK \[Run ll\]"
check_message_with_newline_in_output "ansible-deployer run --task task_with_ansible_fail --stage testing --infrastructure testInfra --raw-runner-output" ".*\n\n\nTASK \[Run ll\]"

echo -e "   ___ ____                      _               _\n  / _ \___ \ __ _            ___| |__   ___  ___| | ___ __ _   _ _ __\n | | | |__) / _\` |  _____   / __| '_ \ / _ \/ __| |/ / '__| | | | '_ \ \n | |_| / __/ (_| | |_____| | (__| | | |  __/ (__|   <| |  | |_| | | | |\n  \___/_____\__,_|          \___|_| |_|\___|\___|_|\_\_|   \__,_|_| |_|\n \n  _ _           _ _                 _   _\n | (_)_ __ ___ (_) |_    ___  _ __ | |_(_) ___  _ __\n | | | '_ \` _ \| | __|  / _ \| '_ \| __| |/ _ \| '_ \ \n | | | | | | | | | |_  | (_) | |_) | |_| | (_) | | | |\n |_|_|_| |_| |_|_|\__|  \___/| .__/ \__|_|\___/|_| |_|\n                             |_|\n"
# Check --limit option
check_message_in_output "ansible-deployer run --task task_with_limit --stage testing --infrastructure testInfra2 --limit xyzHost4" "ERROR\! Specified inventory, host pattern and/or --limit leaves us with no hosts to target."
check_message_in_output "ansible-deployer run --task task_without_limit --stage testing --infrastructure testInfra --limit testHost1" "\[CRITICAL\]: Limit testHost1 is not available for task task_without_limit."
check_message_in_output "ansible-deployer run --task task_exec_bin_true --stage prod --infrastructure testInfra --limit testHost1" "\[CRITICAL\]: Limit testHost1 is not available for task task_exec_bin_true."
## Multiple hosts in limit
check_run_ok "ansible-deployer run --task task_with_limit --stage testing --infrastructure testInfra2 --limit xyzHosts"
## --check-mode overriding --limit disabling
check_run_ok "ansible-deployer run --task task_without_limit --stage testing --infrastructure testInfra --limit testHost1 --check-mode"

# Check if deployer exits on 1st play item fail
check_message_in_output "ansible-deployer run --task task_with_ansible_fail --stage testing --infrastructure testInfra" "\[ERROR\]: \"ansible-playbook -i ./test_infra1_inv.yaml runll.yaml -v\" failed due to"
check_message_not_in_output "ansible-deployer run --task task_with_ansible_fail --stage testing --infrastructure testInfra" "\[INFO\]: \"ansible-playbook -i ./test_infra1_inv.yaml runBinTrue.yaml -v\" ran succesfully"

# Check --keep-locked option
check_message_in_output "ansible-deployer run --task task_exec_bin_true --stage testing --infrastructure testInfra --keep-locked --debug" "\[DEBUG\]: Keep locked infra testInfra:testing ."
check_run_ok "ansible-deployer unlock --stage testing --infrastructure testInfra"

echo -e "   ___ ____                      _               _\n  / _ \___ \ __ _            ___| |__   ___  ___| | ___ __ _   _ _ __\n | | | |__) / _\` |  _____   / __| '_ \ / _ \/ __| |/ / '__| | | | '_ \ \n | |_| / __/ (_| | |_____| | (__| | | |  __/ (__|   <| |  | |_| | | | |\n  \___/_____\__,_|          \___|_| |_|\___|\___|_|\_\_|   \__,_|_| |_|\n \n      _                               _                                                   _\n  ___| |__   _____      __  ___ _   _| |__   ___ ___  _ __ ___  _ __ ___   __ _ _ __   __| |\n / __| '_ \ / _ \ \ /\ / / / __| | | | '_ \ / __/ _ \| '_ \` _ \| '_ \` _ \ / _\` | '_ \ / _\` |\n \__ \ | | | (_) \ V  V /  \__ \ |_| | |_) | (_| (_) | | | | | | | | | | | (_| | | | | (_| |\n |___/_| |_|\___/ \_/\_/   |___/\__,_|_.__/ \___\___/|_| |_| |_|_| |_| |_|\__,_|_| |_|\__,_|\n"
# Check show subcommand
check_message_in_output "ansible-deployer show" "Available infrastructures:"
check_message_in_output "ansible-deployer show" "Available tasks:"
check_message_in_output "ansible-deployer show all" "Available infrastructures:"
check_message_in_output "ansible-deployer show all" "Available tasks:"
check_message_in_output "ansible-deployer show infra" "Available infrastructures:"
check_message_in_output "ansible-deployer show task" "Available tasks:"

echo -e "   ___ ____                      _               _\n  / _ \___ \ __ _            ___| |__   ___  ___| | ___ __ _   _ _ __\n | | | |__) / _\` |  _____   / __| '_ \ / _ \/ __| |/ / '__| | | | '_ \ \n | |_| / __/ (_| | |_____| | (__| | | |  __/ (__|   <| |  | |_| | | | |\n  \___/_____\__,_|          \___|_| |_|\___|\___|_|\_\_|   \__,_|_| |_|\n \n                            _         _\n  _ __   ___ _ __ _ __ ___ (_)___ ___(_) ___  _ __  ___\n | '_ \ / _ \ '__| '_ \` _ \| / __/ __| |/ _ \| '_ \/ __|\n | |_) |  __/ |  | | | | | | \__ \__ \ | (_) | | | \__ \ \n | .__/ \___|_|  |_| |_| |_|_|___/___/_|\___/|_| |_|___/\n |_|\n"
# Check multiple system groups in acl_group
check_run_ok "ansible-deployer run --task task_with_multi_groups --stage testing --infrastructure testInfra"
check_message_in_output "ansible-deployer run --task task_with_multi_groups_fail --stage testing --infrastructure testInfra" "\[CRITICAL\]: Task forbidden"

# Try execution of task without permissions
if [ $UID -ne 0 ]
then
	check_message_in_output "ansible-deployer run --task root_only_task --infrastructure testInfra --stage testing" "\[CRITICAL\]: Task forbidden"
else
	check_message_in_output "ansible-deployer run --task non_root_task --infrastructure testInfra --stage testing" "\[CRITICAL\]: Task forbidden"
fi

