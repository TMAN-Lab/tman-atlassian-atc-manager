#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: will.shi@tman.ltd

import os
import sys
import argparse
from atlassian_atc_manager.utils.appConfig import AppConfig


class OptObj(object):
    def __init__(self, str_kv):
        self.name = str_kv.get("name")
        self.metavar = str_kv.get("metavar")
        self.action = str_kv.get("action")
        self.help = str_kv.get("help")
        self.type = str_kv.get("type")
        self.choices = str_kv.get("choices")


class OptItems(object):
    def __init__(self):
        jira_plugins = [
            "xray",
            # "zephyr-scale"
        ]
        self.jira_plugin = OptObj({
            "name": "--jira-plugin",
            "metavar": "<{}>".format("|".join(jira_plugins)),
            "action": "store",
            "help": "target test management tool on Jira",
            "type": str,
            "choices": jira_plugins
        })
        jira_hosting_types = [
            "cloud",
            "dc"
        ]
        self.jira_hosting = OptObj({
            "name": "--jira-hosting",
            "metavar": "<{}>".format("|".join(jira_hosting_types)),
            "action": "store",
            "help": "Jira hosting type (supports cloud, data-center)",
            "type": str,
            "choices": jira_hosting_types
        })
        self.jira_site = OptObj({
            "name": "--jira-site",
            "metavar": "<URL>",
            "action": "store",
            "help": "Jira site URL (e.g. https://yourcompany.atlassian.net)",
            "type": str
        })
        self.jira_user = OptObj({
            "name": "--jira-user",
            "metavar": "<USERNAME>",
            "action": "store",
            "help": "specify the Jira username for authentication",
            "type": str
        })
        self.jira_token = OptObj({
            "name": "--jira-token",
            "metavar": "<TOKEN>",
            "action": "store",
            "help": "Jira API token for authentication",
            "type": str
        })
        self.test_report = OptObj({
            "name": "--test-report",
            "metavar": "<REPORT_FILE>",
            "action": "store",
            "help": "specify the location of the test report file(supports formats such as JUnit, XML, HTML, etc.)",
            "type": str
        })
        self.jira_project = OptObj({
            "name": "--jira-project",
            "metavar": "<PROJECT_KEY>",
            "action": "store",
            "help": "Jira project key (e.g. \"TEST\")",
            "type": str
        })
        self.test_path = OptObj({
            "name": "--test-path",
            "metavar": "<TEST_CODE_PATH>",
            "action": "store",
            "default": ".",
            "help": "path to a test file or folder (supports .py, .java, .robot)",
            "type": str
        })
        self.config_overwrite = OptObj({
            "name": "--overwrite",
            "action": "store_true",
            "help": "the config file is exsited. Re-config and overwrite it"
        })
        self.xray_client_id = OptObj({
            "name": "--xray-client-id",
            "metavar": "<CLIENT_ID>",
            "action": "store",
            "help": "XRAY Cloud client id for authentication"
        })
        self.xray_client_secret = OptObj({
            "name": "--xray-client-secret",
            "metavar": "<CLIENT_SECRET>",
            "action": "store",
            "help": "XRAY Cloud client secret for authentication"
        })


class AppArgumentParser(argparse.ArgumentParser):
    def error(self, message: str):
        self.print_help(sys.stderr)
        sys.exit(1)


def add_argument_to_sub_parser(sub_parser_item, arg_item, is_required):
    sub_parser_item.add_argument(
        arg_item.name,
        metavar=arg_item.metavar,
        action=arg_item.action,
        help="{} : {}".format(arg_item.help, " | ".join(arg_item.choices)) if arg_item.choices else arg_item.help,
        type=arg_item.type,
        choices=arg_item.choices,
        required=is_required
    )


class AppParser(object):
    def __init__(self):
        self.app_config = AppConfig()
        self.parser = AppArgumentParser(description="")

        sub_parsers = self.parser.add_subparsers(
            dest="command",
            help=""
        )

        arg_items = OptItems()

        sub_parsers.add_parser(
            "show-version",
            help="display version info for this tool and your Python runtime"
        )

        sub_parsers.add_parser(
            "show-variables",
            help="show all supported environment variables"
        )

        sub_parsers.add_parser(
            "show-config",
            help="show config"
        )

        sub_parser_config_cred = sub_parsers.add_parser(
            "config-cred",
            help="set and save Jira credentials/config (project, token, etc.)"
        )
        if os.path.exists(self.app_config.app_config_file):
            sub_parser_config_cred.add_argument(
                arg_items.config_overwrite.name,
                action=arg_items.config_overwrite.action,
                help=arg_items.config_overwrite.help,
                required=True
            )
        add_argument_to_sub_parser(
            sub_parser_config_cred,
            arg_items.jira_plugin,
            is_required=False if self.app_config.app_config_yaml.get("jira_plugin") else True
        )
        add_argument_to_sub_parser(
            sub_parser_config_cred,
            arg_items.jira_project,
            is_required=False if self.app_config.app_config_yaml.get("jira_project") else True
        )
        add_argument_to_sub_parser(
            sub_parser_config_cred,
            arg_items.jira_hosting,
            is_required=False
        )
        add_argument_to_sub_parser(
            sub_parser_config_cred,
            arg_items.jira_site,
            is_required=False if self.app_config.app_config_yaml.get("jira_site") else True
        )
        add_argument_to_sub_parser(
            sub_parser_config_cred,
            arg_items.jira_user,
            is_required=False if self.app_config.app_config_yaml.get("jira_user") else True
        )
        add_argument_to_sub_parser(
            sub_parser_config_cred,
            arg_items.jira_token,
            is_required=False if self.app_config.app_config_yaml.get("jira_token") else True
        )
        hosting_is_cloud = True if self.app_config.get_config_from_env(key="jira_hosting") == "cloud" else False
        plugin_is_xray = True if self.app_config.get_config_from_env(key="jira_plugin") == "xray" else False
        if hosting_is_cloud and plugin_is_xray:
            add_argument_to_sub_parser(
                sub_parser_config_cred,
                arg_items.xray_client_id,
                is_required=False if self.app_config.app_config_yaml.get("xray_client_id") else True
            )
            add_argument_to_sub_parser(
                sub_parser_config_cred,
                arg_items.xray_client_secret,
                is_required=False if self.app_config.app_config_yaml.get("xray_client_secret") else True
            )

        sub_parser_sync_case = sub_parsers.add_parser(
            "extract-case",
            help="extract test cases from code and sync them to Jira (Xray, Zephyr Scale, etc.)"
        )
        add_argument_to_sub_parser(
            sub_parser_sync_case,
            arg_items.test_path,
            is_required=True
        )
        add_argument_to_sub_parser(
            sub_parser_sync_case,
            arg_items.jira_plugin,
            is_required=False if self.app_config.get_config_from_env("jira_plugin") else True
        )
        add_argument_to_sub_parser(
            sub_parser_sync_case,
            arg_items.jira_project,
            is_required=False if self.app_config.get_config_from_env("jira_project") else True
        )
        add_argument_to_sub_parser(
            sub_parser_sync_case,
            arg_items.jira_hosting,
            is_required=False if self.app_config.get_config_from_env("jira_hosting") else True
        )
        add_argument_to_sub_parser(
            sub_parser_sync_case,
            arg_items.jira_site,
            is_required=False if self.app_config.get_config_from_env("jira_site") else True
        )
        add_argument_to_sub_parser(
            sub_parser_sync_case,
            arg_items.jira_user,
            is_required=False if self.app_config.get_config_from_env("jira_user") else True
        )
        add_argument_to_sub_parser(
            sub_parser_sync_case,
            arg_items.jira_token,
            is_required=False if self.app_config.get_config_from_env("jira_token") else True
        )
        if hosting_is_cloud and plugin_is_xray:
            add_argument_to_sub_parser(
                sub_parser_sync_case,
                arg_items.xray_client_id,
                is_required=False if self.app_config.app_config_yaml.get("xray_client_id") else True
            )
            add_argument_to_sub_parser(
                sub_parser_sync_case,
                arg_items.xray_client_secret,
                is_required=False if self.app_config.app_config_yaml.get("xray_client_secret") else True
            )

        # sub_parser_mark_result = sub_parsers.add_parser(
        #     "mark-result",
        #     help="mark test case execution results to Jira."
        # )
        # add_argument_to_sub_parser(sub_parser_mark_result, arg_items.platform, is_required=True)


if __name__ == "__main__":
    print("🚀 This is CLI script")
