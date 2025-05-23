#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: will.shi@tman.ltd


import os
# import shutil
import sys
import pkg_resources
# import requests
import yaml
# from tabulate import tabulate
from atlassian_atc_manager.utils.appLogger import AppLogger
from atlassian_atc_manager.utils.appExractor import AppExtractor
from atlassian_atc_manager.utils.appConfig import AppConfig
from atlassian_atc_manager.cli.appCli import OptItems
from atlassian_atc_manager.utils.appXrayDC import AppXrayDC
from atlassian_atc_manager.utils.appXrayCloud import AppXrayCloud
# from crontab import CronTab
# from crontab import CronItem


def print_tree(start_path, indent=""):
    if indent == "":
        print(os.path.basename(start_path))
    for idx, item in enumerate(os.listdir(start_path)) if os.path.isdir(start_path) else {}:
        path = os.path.join(start_path, item)
        connector = "├── " if idx < len(os.listdir(start_path)) - 1 else "└── "
        print(indent + connector + item)
        if os.path.isdir(path):
            new_indent = indent + ("│   " if idx < len(os.listdir(start_path)) - 1 else "    ")
            print_tree(path, new_indent)
    return True


class AppApi(object):
    def __init__(self, app_args):
        self.app_config = AppConfig()
        self.app_args = app_args
        self.app_logger = AppLogger()
        self.app_test_plugin = None
        arg_jira_plugin = str(self.app_config.get_config_from_input_and_env("jira_plugin", self.app_args)).lower()
        arg_jira_hosting = str(self.app_config.get_config_from_input_and_env("jira_hosting", self.app_args)).lower()
        if arg_jira_plugin == "xray" and arg_jira_hosting == "cloud":
            self.app_test_plugin = AppXrayCloud(
                jira_site=self.app_config.get_config_from_input_and_env("jira_site", self.app_args),
                jira_user=self.app_config.get_config_from_input_and_env("jira_user", self.app_args),
                jira_token=self.app_config.get_config_from_input_and_env("jira_token", self.app_args),
                jira_project=self.app_config.get_config_from_input_and_env("jira_project", self.app_args),
                xray_client_id=self.app_config.get_config_from_input_and_env("xray_client_id", self.app_args),
                xray_client_secret=self.app_config.get_config_from_input_and_env("xray_client_secret", self.app_args)
            )
        elif arg_jira_plugin == "xray" and arg_jira_hosting == "dc":
            self.app_test_plugin = AppXrayDC(
                jira_site=self.app_config.get_config_from_input_and_env("jira_site", self.app_args),
                jira_token=self.app_config.get_config_from_input_and_env("jira_token", self.app_args),
                jira_project=self.app_config.get_config_from_input_and_env("jira_project", self.app_args)
            )

    def show_version(self):
        try:
            pkg_version = pkg_resources.get_distribution(self.app_config.pkg_name).version
        except pkg_resources.DistributionNotFound:
            pkg_version = "0.1"
        version_str_install = "{} [{}] version: {}".format(
            self.app_config.cmd_name,
            self.app_config.pkg_name,
            pkg_version
        )
        version_str_python = "Python version: {}".format(sys.version)
        version_str_tag = "\u00AF" * max(
            len(version_str_install),
            len(version_str_python.split("\n")[0])
        )
        print("\n".join([
            version_str_install,
            version_str_tag,
            version_str_python,
            version_str_tag,
        ]))
        return True

    def show_variables(self):
        opt_items = OptItems()
        for k, v in opt_items.__dict__.items():
            if k == "config_overwrite":
                continue
            print("\t".join([
                self.app_config.env_prefix + k.upper(),
                "{} : {}".format(v.help, " | ".join(v.choices)) if v.choices else v.help
            ]))
        return True

    def show_config(self):
        for k, v in self.app_config.app_config_yaml.items():
            if "_token" in k or "_secret" in k:
                self.app_logger.tab_success("{}: ******".format(k))
            else:
                self.app_logger.tab_success("{}: {}".format(k, v))
        return True

    def config_cred(self):
        config_json = dict()
        for key, value in self.app_args.items():
            if key not in ["command", "overwrite"] and value:
                config_json[key] = value
        self.app_config.create_config_file(
            config_file_json=config_json,
            force=True
        )
        self.app_logger.success("Create/Update config file:")
        self.show_config()
        return True

    def __extract_case(self, file_path=None, print_file_tree=True):
        if file_path is None:
            if self.app_args.get("test_path"):
                file_path = os.path.abspath(self.app_args.get("test_path"))
            else:
                file_path = self.app_config.app_workdir
        if print_file_tree:
            self.app_logger.launch("Start to check and extract below files:")
            print_tree(file_path)
        extractor = AppExtractor()
        if os.path.isfile(file_path) and str(file_path).endswith(".py"):
            self.app_logger.launch(file_path)
            case_repo_path = extractor.check_get_test_set_path(file_path)[:-1]
            case_repo = "/".join(case_repo_path)
            for case_title, case_action in extractor.extract_from_python_script_file(file_path).items():
                self.app_logger.tab_success(case_title)
                # print("🐍 Test Case: {}".format(case_title))
                # print("".join(case_action))
                self.app_test_plugin.create_update_case(
                    code_url=self.app_config.git_repo_url,
                    code_repo=case_repo,
                    code_path=case_title,
                    code_lang="python",
                    code_case="".join(case_action)
                )
        elif os.path.isfile(file_path) and str(file_path).endswith(".java"):
            self.app_logger.launch(file_path)
            case_repo_path = extractor.check_get_test_set_path(file_path)[:-1]
            case_repo = "/".join(case_repo_path)
            for case_title, case_action in extractor.extract_from_java_script_file(file_path).items():
                self.app_logger.tab_success(case_title)
                # print("☕️ Test Case: {}".format(case_title))
                # print("".join(case_action))
                self.app_test_plugin.create_update_case(
                    code_url=self.app_config.git_repo_url,
                    code_repo=case_repo,
                    code_path=case_title,
                    code_lang="java",
                    code_case="".join(case_action)
                )
        elif os.path.isfile(file_path) and str(file_path).endswith(".robot"):
            self.app_logger.launch(file_path)
            case_repo_path = extractor.check_get_test_set_path(file_path)[:-1]
            case_repo = "/".join(case_repo_path)
            for case_title, case_action in extractor.extract_from_robot_script_file(file_path).items():
                self.app_logger.tab_success(case_title)
                # print("🤖 Test Case: {}".format(case_title))
                # print("".join(case_action))
                self.app_test_plugin.create_update_case(
                    code_url=self.app_config.git_repo_url,
                    code_repo=case_repo,
                    code_path=case_title,
                    code_lang="none",
                    code_case="".join(case_action)
                )
        elif os.path.isdir(file_path):
            for item in os.listdir(file_path):
                item_path = os.path.join(file_path, item)
                self.__extract_case(item_path, print_file_tree=False)
        return True

    def extract_case(self, file_path=None):
        self.__extract_case(file_path=file_path, print_file_tree=True)
        self.app_logger.success("Total {} requests to remote services via rest api".format(
            self.app_test_plugin.total_rest_requests
        ))
        self.app_logger.tab_success("Create cases: {}".format(self.app_test_plugin.total_create_cases))
        self.app_logger.tab_success("Update cases: {}".format(self.app_test_plugin.total_update_cases))
        return True


if __name__ == "__main__":
    print("🚀 This is an API package")
