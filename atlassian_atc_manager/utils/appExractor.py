#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: will.shi@tman.ltd

import os
from atlassian_atc_manager.utils.appConfig import AppConfig


class AppExtractor(object):
    def __init__(self):
        self.app_config = AppConfig()
        self.repo_name = self.app_config.get_repo_name_from_git_url()

    def __extract_path(self, path_string):
        paths = list()
        path_split = os.path.split(path_string)
        if len(path_split[-1]):
            paths.append(path_split[-1])
            paths += self.__extract_path(path_split[0])
        return paths

    def check_get_test_set_path(self, test_file_path):
        test_set_path = list()
        test_file_ext = os.path.splitext(test_file_path)[-1]
        if self.repo_name:
            test_set_path.append(self.repo_name)
        else:
            test_set_path.append(os.path.basename(self.app_config.app_workdir))
        path_in_repo = test_file_path.split(self.app_config.app_workdir)[-1]
        extracted_path = self.__extract_path(path_in_repo.split(test_file_ext)[0])
        extracted_path.reverse()
        test_set_path += extracted_path
        return test_set_path

    def extract_from_python_script_file(self, test_file_path):
        test_set_path = self.check_get_test_set_path(test_file_path)
        in_class = False
        class_indent_level = None
        in_method = False
        method_indent_level = None
        method_path = test_set_path
        test_cases = dict()
        test_case_title = None

        with open(test_file_path, 'r', encoding='utf-8') as f:
            content_lines = f.readlines()

        for line_text in content_lines:
            line_stripped_text = line_text.strip()
            line_left_stripped_text = line_text.lstrip()
            line_indent = len(line_text) - len(line_left_stripped_text)

            if not in_class and line_stripped_text.startswith("class "):
                in_class = True
                class_indent_level = line_indent
                class_name = line_stripped_text.replace("class ", "").split("(")[0]
                method_path.append(class_name)
            elif in_class and line_stripped_text and not line_stripped_text.startswith("#") and line_indent <= class_indent_level:
                in_class = False
                method_path = test_set_path
                if line_stripped_text.startswith("class "):
                    in_class = True
                    class_indent_level = line_indent
                    class_name = line_stripped_text.replace("class ", "").split("(")[0]
                    method_path.append(class_name)

            if not in_method and line_stripped_text.startswith("def test_"):
                in_method = True
                method_indent_level = line_indent
                method_name = line_stripped_text.replace("def ", "").split("(")[0]
                test_case_title = ".".join([
                    ".".join(method_path),
                    method_name
                ])
                test_cases[test_case_title] = list()
                test_cases[test_case_title].append(line_text)
            elif in_method and line_stripped_text and not line_stripped_text.startswith("#") and line_indent <= method_indent_level:
                in_method = False
                if line_stripped_text.startswith("def test_"):
                    in_method = True
                    method_indent_level = line_indent
                    method_name = line_stripped_text.replace("def ", "").split("(")[0]
                    test_case_title = ".".join([
                        ".".join(method_path),
                        method_name
                    ])
                    test_cases[test_case_title] = list()
                    test_cases[test_case_title].append(line_text)
            elif in_method and test_case_title:
                test_cases[test_case_title].append(line_text)
        return test_cases

    @staticmethod
    def __extract_from_java_test_class(method_path, code_blocks, test_cases):
        test_case_title = None
        test_code_block = list()
        brace_count = 0
        is_test_code = None
        for line_text in code_blocks:
            line_stripped_text = line_text.strip()
            if brace_count >= 1 and "{" not in line_stripped_text and "}" not in line_stripped_text:
                test_code_block.append(line_text)
            else:
                char_text = ""
                for i, char in enumerate(line_text):
                    char_text += char
                    if char == "{":
                        brace_count += 1
                        if brace_count == 2 and test_case_title is None:
                            is_test_code = True
                            test_case_title_split = "{}{}".format(
                                "".join(test_code_block),
                                char_text
                            ).split()
                            method_name = test_case_title_split[-2]
                            test_case_title = "{}.{}".format(method_path, method_name.split("(")[0])
                    elif char == "}":
                        brace_count -= 1
                        if brace_count == 1:
                            is_test_code = False
                            break
                if brace_count >= 2:
                    test_code_block.append(char_text)
                if is_test_code is False and test_case_title:
                    test_cases[test_case_title] = test_code_block
                    test_code_block = list()
                    test_case_title = None

    def extract_from_java_script_file(self, test_file_path):
        test_set_path = self.check_get_test_set_path(test_file_path)
        test_cases = dict()
        is_class_code = False
        method_path = test_set_path
        test_case_title = None
        is_test_code = False
        test_code_block = list()
        brace_count = 0

        with open(test_file_path, 'r', encoding='utf-8') as f:
            content_lines = f.readlines()

        for line_text in content_lines:
            line_stripped_text = line_text.strip()
            if line_stripped_text.startswith("@Test"):
                is_test_code = True
                continue
            elif is_test_code and "{" not in line_stripped_text and "}" not in line_stripped_text:
                test_code_block.append(line_text)
            elif is_test_code:
                char_text = ""
                for i, char in enumerate(line_text):
                    char_text += char
                    if char == "{":
                        brace_count += 1
                        if brace_count == 1 and test_case_title is None:
                            test_case_title_split = "{}{}".format(
                                "".join(test_code_block),
                                char_text
                            ).split()
                            if "class" in test_case_title_split[:2]:
                                is_class_code = True
                                class_index_num = test_case_title_split.index("class")
                                class_name = test_case_title_split[class_index_num + 1]
                                test_case_title = ".".join([
                                    ".".join(method_path),
                                    class_name
                                ])
                            else:
                                method_name = test_case_title_split[-2]
                                test_case_title = ".".join([
                                    ".".join(method_path),
                                    method_name.split("(")[0]
                                ])
                    elif char == "}":
                        brace_count -= 1
                        if brace_count == 0:
                            is_test_code = False
                            break
                test_code_block.append(char_text)
                if not is_test_code:
                    if is_class_code:
                        self.__extract_from_java_test_class(
                            method_path=test_case_title,
                            code_blocks=test_code_block,
                            test_cases=test_cases
                        )
                    else:
                        test_cases[test_case_title] = test_code_block
                        test_code_block = list()
                        test_case_title = None
        return test_cases

    def extract_from_robot_script_file(self, test_file_path):
        test_set_path = self.check_get_test_set_path(test_file_path)
        in_test_section = False
        in_test_case = False
        case_indent_level = None
        case_path = test_set_path
        test_cases = dict()
        test_case_title = None

        with open(test_file_path, 'r', encoding='utf-8') as f:
            content_lines = f.readlines()

        for line_text in content_lines:
            line_stripped_text = line_text.strip()
            line_left_stripped_text = line_text.lstrip()
            line_indent = len(line_text) - len(line_left_stripped_text)

            if line_stripped_text.lower().startswith("*** test cases ***"):
                in_test_section = True
                continue
            if in_test_section:
                if line_stripped_text.lower().startswith("***"):
                    break
                if not in_test_case and line_stripped_text.lower().startswith("["):
                    continue
                elif not in_test_case and line_stripped_text:
                    in_test_case = True
                    case_indent_level = line_indent
                    test_case_title = ".".join([
                        ".".join(case_path),
                        line_stripped_text
                    ])
                    test_cases[test_case_title] = list()
                    test_cases[test_case_title].append(line_text)
                elif in_test_case and line_stripped_text and line_indent <= case_indent_level:
                    test_case_title = ".".join([
                        ".".join(case_path),
                        line_stripped_text
                    ])
                    test_cases[test_case_title] = list()
                    test_cases[test_case_title].append(line_text)
                elif in_test_case and test_case_title:
                    test_cases[test_case_title].append(line_text)
        return test_cases


if __name__ == "__main__":
    print("🚀 This is an extractor package")
