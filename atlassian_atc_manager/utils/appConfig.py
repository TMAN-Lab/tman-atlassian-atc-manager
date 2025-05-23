#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: will.shi@tman.ltd


import os
import yaml
from urllib.parse import urlparse, urlunparse


def clean_url(url):
    parsed = urlparse(url)
    netloc = parsed.netloc.split("@")[-1]
    return urlunparse((
        parsed.scheme,
        netloc,
        parsed.path.rstrip(".git"),
        "",
        "",
        ""
    ))


class AppConfig(object):
    def __init__(self):
        self.pkg_name = "atlassian-auto-test-case-manager".replace("-", "_")
        self.cmd_name = "atlas-atc-manager"
        self.app_name = self.cmd_name.replace("-", "_")
        self.env_prefix = self.app_name.upper() + "_"
        self.app_config_file = os.path.join(
            os.path.expanduser("~"),
            ".{}".format(self.app_name),
            "credential.conf"
        )
        self.app_config_yaml = dict()
        if os.path.exists(self.app_config_file):
            with open(self.app_config_file, "r", encoding="utf-8") as f:
                self.app_config_yaml = yaml.safe_load(f.read())
            if not self.app_config_yaml:
                self.app_config_yaml = dict()
        self.app_workdir = os.getcwd()
        self.app_workdir_name = os.path.basename(self.app_workdir)
        self.app_workdir_git_config = os.path.join(self.app_workdir, ".git", "config")
        self.git_repo_url = None
        if os.path.exists(self.app_workdir_git_config):
            with open(self.app_workdir_git_config, 'r', encoding='utf-8') as f:
                content = f.read()
            for line_text in content.split("\n"):
                if "url " in line_text:
                    self.git_repo_url = clean_url(line_text.split()[-1])
                    break

    def get_repo_name_from_git_url(self):
        return str(self.git_repo_url).split("/")[-1] if self.git_repo_url else None

    def create_config_file(self, config_file_json: dict, force=False):
        config_exists = os.path.exists(self.app_config_file)
        if config_exists and force:
            for config_key, config_value in config_file_json.items():
                self.app_config_yaml[config_key] = config_value
            with open(self.app_config_file, "w", encoding="utf-8") as f:
                f.write(yaml.dump(self.app_config_yaml))
        elif not config_exists:
            os.makedirs(os.path.join(os.path.expanduser("~"), ".{}".format(self.app_name)), exist_ok=True)
            self.app_config_yaml = config_file_json
            with open(self.app_config_file, "w", encoding="utf-8") as f:
                f.write(yaml.dump(self.app_config_yaml))

    def get_config_from_input_and_env(self, key: str, input_args):
        if input_args.get(key):
            return input_args.get(key)
        else:
            return self.get_config_from_env(key)

    def get_config_from_env(self, key: str):
        """
        input parameter > env variable > config file
        :param key:
        :return:
        """
        env_key = self.env_prefix + key.upper()
        yaml_lower_key = key.lower()
        yaml_upper_key = key.upper()
        if os.getenv(env_key):
            return os.getenv(env_key)
        elif self.app_config_yaml.get(yaml_upper_key):
            return self.app_config_yaml.get(yaml_upper_key)
        elif self.app_config_yaml.get(yaml_lower_key):
            return self.app_config_yaml.get(yaml_lower_key)
        else:
            return None


if __name__ == "__main__":
    print("🚀 This is a config package")
