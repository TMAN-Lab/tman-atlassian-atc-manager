#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: will.shi@tman.ltd


import requests
from atlassian_atc_manager.utils.appLogger import AppLogger


class XrayDcCustomFieldKeys(object):
    def __init__(self):
        self.test_repo_path = "test-repository-path-custom-field"
        self.test_type = "test-type-custom-field"
        self.test_steps = "manual-test-steps-custom-field"


class AppXrayDC(object):
    def __init__(self, jira_site, jira_token, jira_project):
        self.app_logger = AppLogger()
        self.session = requests.session()
        self.jira_site = jira_site
        self.jira_api_version = "2"
        self.jira_base_url = "{}/rest/api/{}".format(self.jira_site, self.jira_api_version)
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(jira_token)
        }
        self.jira_project_key = jira_project
        self.jira_test_issue_type_id = None
        self.xray_custom_fields = dict()
        self.case_description_prefix = "TMAN AutoTestCase Sync from Git Repository:"
        self.xray_cf_keys = XrayDcCustomFieldKeys()
        self.xray_case_repo_home = "/AutoTestCaseSync"
        self.total_rest_requests = 0
        self.total_create_cases = 0
        self.total_update_cases = 0

    def __get_xray_project_test_issue_type_id(self):
        url = "{}/project/{}".format(self.jira_base_url, self.jira_project_key)
        self.total_rest_requests += 1
        rsp = self.session.get(url=url, headers=self.headers)
        assert rsp.status_code == 200, "{} {}".format(rsp.status_code, rsp.json() if rsp.json() else rsp.content)
        for item in rsp.json().get("issueTypes"):
            if item.get("description") == "Represents a Test":
                self.jira_test_issue_type_id = item.get("id")
                break
        return self.jira_test_issue_type_id

    def __get_xray_custom_fields(self):
        if self.jira_test_issue_type_id is None:
            self.__get_xray_project_test_issue_type_id()
        url = "{}/field".format(self.jira_base_url)
        self.total_rest_requests += 1
        rsp = self.session.get(url=url, headers=self.headers)
        assert rsp.status_code == 200, "{} {}".format(rsp.status_code, rsp.json() if rsp.json() else rsp.content)
        for item in rsp.json():
            schema_custom = item["schema"]["custom"] if item.get("schema") and item["schema"].get("custom") else None
            if str(schema_custom).startswith("com.xpandit.plugins.xray:"):
                xray_cf_key = str(schema_custom).split(":")[-1]
                xray_cf_id = item.get("id")
                self.xray_custom_fields[xray_cf_key] = xray_cf_id
        return self.xray_custom_fields

    def __search_case_by_summary(self, case_summary):
        if not self.xray_custom_fields:
            self.__get_xray_custom_fields()
        if self.jira_test_issue_type_id is None:
            self.__get_xray_project_test_issue_type_id()
        url = "{}/search".format(self.jira_base_url)
        body = {
            "jql": "project = {} AND issuetype in ({}) AND summary ~ \"{}\" AND description ~ \"{}\"".format(
                self.jira_project_key,
                self.jira_test_issue_type_id,
                case_summary,
                self.case_description_prefix
            ),
            "fields": [
                "description",
                self.xray_custom_fields.get(self.xray_cf_keys.test_repo_path),
                self.xray_custom_fields.get(self.xray_cf_keys.test_type),
                self.xray_custom_fields.get(self.xray_cf_keys.test_steps)
            ]
        }
        self.total_rest_requests += 1
        rsp = self.session.post(url=url, headers=self.headers, json=body)
        assert rsp.status_code == 200, "{} {}".format(rsp.status_code, rsp.json() if rsp.json() else rsp.content)
        results = rsp.json()
        return results.get("issues") if results.get("issues") else []

    def __update_case(self, case_id, case_description, case_repo, case_type,
                      step_action, step_data, step_expected):
        url = "{}/issue/{}".format(self.jira_base_url, case_id)
        body = {
            "fields": {
                "description": case_description,
                self.xray_custom_fields.get(self.xray_cf_keys.test_repo_path): case_repo,
                self.xray_custom_fields.get(self.xray_cf_keys.test_type): case_type,
                self.xray_custom_fields.get(self.xray_cf_keys.test_steps): {
                    "steps": [
                        {
                            "index": 1,
                            "fields": {
                                "Action": step_action,
                                "Data": step_data,
                                "Expected Result": step_expected
                            }
                        }
                    ]
                },
            }
        }
        self.total_rest_requests += 1
        rsp = self.session.put(url=url, headers=self.headers, json=body)
        assert rsp.status_code == 204, "{} {}\n{}".format(
            rsp.status_code,
            rsp.json() if rsp.json() else rsp.content,
            body
        )
        return True

    def __create_case(self, case_summary, case_description, case_repo, case_type,
                      step_action, step_data, step_expected):
        url = "{}/issue".format(self.jira_base_url)
        body = {
            "fields": {
                "project": {
                    "key": self.jira_project_key
                },
                "summary": case_summary,
                "description": case_description,
                "issuetype": {
                    "id": self.jira_test_issue_type_id
                },
                self.xray_custom_fields.get(self.xray_cf_keys.test_repo_path): case_repo,
                self.xray_custom_fields.get(self.xray_cf_keys.test_type): case_type,
                self.xray_custom_fields.get(self.xray_cf_keys.test_steps): {
                    "steps": [
                        {
                            "index": 1,
                            "fields": {
                                "Action": step_action,
                                "Data": step_data,
                                "Expected Result": step_expected
                            }
                        }
                    ]
                },
            }
        }
        self.total_rest_requests += 1
        rsp = self.session.post(url=url, headers=self.headers, json=body)
        assert rsp.status_code == 201, "{} {}".format(rsp.status_code, rsp.json() if rsp.json() else rsp.content)
        return True

    def create_update_case(self, code_url, code_repo, code_path, code_lang, code_case):
        if not self.xray_custom_fields:
            self.__get_xray_custom_fields()
        if self.jira_test_issue_type_id is None:
            self.__get_xray_project_test_issue_type_id()
        step_action = "\n".join([
            "{panel:title=" + code_path + "}",
            "{code:" + code_lang + "}",
            code_case,
            "{code}",
            "{panel}"
        ])
        step_data = ""
        step_expected = "{color:#00875a}PASS{color}"
        case_summary = code_path
        case_description = "{}\n{}".format(self.case_description_prefix, code_url)
        case_repo = "".join([
            self.xray_case_repo_home,
            code_repo
        ]) if str(code_repo).startswith("/") else "/".join([
            self.xray_case_repo_home,
            code_repo
        ])
        case_type = {
            "value": "Manual"
        }
        case_id = None
        for case_item in self.__search_case_by_summary(case_summary):
            case_id = case_item.get("key")
            issue_description = case_item["fields"].get("description")
            issue_description_is_changed = False if issue_description == case_description else True
            if issue_description_is_changed:
                self.app_logger.tab_warning("Update test case description")
            test_repo_path = case_item["fields"].get(self.xray_custom_fields.get(self.xray_cf_keys.test_repo_path))
            test_repo_path_is_changed = False if test_repo_path == case_repo else True
            if test_repo_path_is_changed:
                self.app_logger.tab_warning("Update test case folder")
            test_type = case_item["fields"].get(self.xray_custom_fields.get(self.xray_cf_keys.test_type))
            test_type_is_changed = False if test_type.get("value") == case_type.get("value") else True
            if test_type_is_changed:
                self.app_logger.tab_warning("Update test case type")
            manual_test_steps = case_item["fields"].get(self.xray_custom_fields.get(self.xray_cf_keys.test_steps))
            test_step_is_changed = True \
                if manual_test_steps.get("steps") and manual_test_steps["steps"][0]["fields"]["Action"] != step_action \
                else False
            if test_step_is_changed:
                self.app_logger.tab_warning("Update test case step action")
            if issue_description_is_changed \
                    or test_repo_path_is_changed \
                    or test_type_is_changed \
                    or test_step_is_changed:
                self.total_update_cases += 1
                return self.__update_case(case_id, case_description, case_repo, case_type,
                                          step_action, step_data, step_expected)
        if case_id is None:
            self.app_logger.tab_warning("Create new test case")
            self.total_create_cases += 1
            return self.__create_case(case_summary, case_description, case_repo, case_type,
                                      step_action, step_data, step_expected)
 

if __name__ == "__main__":
    print("🚀 This is an app script of XRAY")
