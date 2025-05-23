#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: will.shi@tman.ltd


# import yaml
import requests
from atlassian_atc_manager.utils.appLogger import AppLogger


def xray_test_code_dumps(raw_test_code):
    return raw_test_code.replace("\n", "\\n").replace('"', '\\\"')


def xray_test_code_loads(xray_test_code):
    return xray_test_code.replace("\\n", "\n").replace('\\\"', '"')


class AppXrayCloud(object):
    def __init__(self, jira_site, jira_user, jira_token, jira_project, xray_client_id, xray_client_secret):
        self.app_logger = AppLogger()
        self.session = requests.session()
        self.jira_headers = {
            "Content-Type": "application/json"
        }
        self.jira_site = jira_site
        self.jira_user = jira_user
        self.jira_token = jira_token
        self.jira_api_version = "3"
        self.jira_base_url = "{}/rest/api/{}".format(self.jira_site, self.jira_api_version)
        self.jira_project_key = jira_project
        self.jira_project_id = None
        self.jira_test_issue_type_id = None
        self.xray_headers = {
            "Content-Type": "application/json"
        }
        self.xray_custom_fields = dict()
        self.case_description_prefix = "TMAN AutoTestCase Sync from Git Repository:"
        self.xray_case_repo_home = "/AutoTestCaseSync"
        self.xray_cloud_api_version = "2"
        self.xray_api_url = "https://xray.cloud.getxray.app"
        self.xray_base_url = "{}/api/v{}".format(self.xray_api_url, self.xray_cloud_api_version)
        self.xray_client_id = xray_client_id
        self.xray_client_secret = xray_client_secret
        self.xray_token = None
        self.xray_test_type = "Generic"
        self.xray_folders_exist = list()
        self.total_rest_requests = 0
        self.total_create_cases = 0
        self.total_update_cases = 0

    def __get_xray_token(self):
        if self.xray_headers.get("Authorization") is None:
            url = "{}/authenticate".format(self.xray_base_url)
            body = {
                "client_id": self.xray_client_id,
                "client_secret": self.xray_client_secret
            }
            self.total_rest_requests += 1
            rsp = self.session.post(url=url, headers=self.xray_headers, json=body)
            assert rsp.status_code == 200, "{} {}".format(rsp.status_code, rsp.json() if rsp.json() else rsp.content)
            self.xray_headers["Authorization"] = "Bearer {}".format(rsp.json())
        return self.xray_headers.get("Authorization")

    def __xray_crud_case(self, request, graphql):
        self.__get_xray_token()
        url = "{}/graphql".format(self.xray_base_url)
        body = {
            "query": graphql
        }
        # print(url)
        # print(graphql)
        self.total_rest_requests += 1
        rsp = self.session.post(url=url, headers=self.xray_headers, json=body)
        assert rsp.status_code == 200, "{} {} {}".format(
            request,
            rsp.status_code,
            rsp.json() if rsp.json() else rsp.content
        )
        return rsp.json()

    def __search_case_by_summary(self, case_summary):
        cases = list()
        graphql = """
        {
            getTests(jql: "project = %s and summary ~ '%s'", limit: 10) {
                results {
                    issueId
                    testType {
                        name
                        kind
                    }
                    unstructured
                    jira(fields: ["key", "summary", "description"])
                    folder { 
                        name
                        path
                    }
                }
            }
        }
        """ % (self.jira_project_key, case_summary)
        rsp = self.__xray_crud_case(request="getTests", graphql=graphql)
        for result in rsp["data"]["getTests"]["results"]:
            if result["jira"].get("summary") == case_summary:
                cases.append(result)
        return cases

    def __update_case_description(self, case_id, code_url):
        url = "{}/issue/{}".format(self.jira_base_url, case_id)
        body = {
            "fields": {
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [{
                        "type": "paragraph",
                        "content": [{
                            "type": "text",
                            "text": self.case_description_prefix
                        }]
                    }, {
                        "type": "paragraph",
                        "content": [{
                            "type": "text",
                            "text": "{}".format(code_url),
                            "marks": [{
                                "type": "link",
                                "attrs": {
                                    "href": "{}".format(code_url)
                                }
                            }]
                        }]
                    }]
                }
            }
        }
        self.total_rest_requests += 1
        rsp = self.session.put(url=url, headers=self.jira_headers, json=body, auth=(self.jira_user, self.jira_token))
        assert rsp.status_code == 204, "{} {}".format(rsp.status_code, rsp.content)
        return True

    def __update_case_folder(self, case_id, case_repo):
        graphql = """
        mutation {
            updateTestFolder(
                issueId: "%s",
                folderPath: "%s"
            ) 
        }
        """ % (case_id, case_repo)
        rsp = self.__xray_crud_case(request="updateTestFolder", graphql=graphql)
        return str(rsp["data"]["updateTestFolder"]).startswith('Test moved to the folder')

    def __update_case_type(self, case_id, case_type):
        graphql = """
        mutation {
            updateTestType(
                issueId: "%s",
                testType: { name: "%s" }
            ) {
                issueId
                jira(fields: ["key"]
            }
        }
        """ % (case_id, case_type)
        rsp = self.__xray_crud_case(request="updateTestType", graphql=graphql)
        return rsp["data"]["updateTestType"]

    def __update_case_definition(self, case_id, case_definition):
        graphql = """
        mutation {
            updateUnstructuredTestDefinition(
                issueId: "%s", 
                unstructured: "%s",
            ) {
                issueId
                jira(fields: ["key"])
            }
        }
        """ % (case_id, case_definition)
        rsp = self.__xray_crud_case(request="updateUnstructuredTestDefinition", graphql=graphql)
        return rsp["data"]["updateUnstructuredTestDefinition"]

    def __check_create_case_folder(self, case_repo):
        self.__get_xray_project_id()
        if case_repo not in self.xray_folders_exist:
            get_graphql = """
            {
                getFolder(
                    projectId: "%s",
                    path: "%s"
                ) {
                    path
                }
            }
            """ % (self.jira_project_id, case_repo)
            get_rsp = self.__xray_crud_case("getFolder", graphql=get_graphql)
            if get_rsp["data"].get("getFolder") is None:
                create_graphql = """
                mutation {
                    createFolder(
                        projectId: "%s",
                        path: "%s"
                    ) {
                        warnings
                    }
                }
                """ % (self.jira_project_id, case_repo)
                self.app_logger.tab_warning("Create test folder")
                create_rsp = self.__xray_crud_case("createFolder", graphql=create_graphql)
                assert len(create_rsp["data"]["createFolder"].get("warnings")) == 0, "{} {}".format(
                    create_rsp.status_code,
                    create_rsp.json() if create_rsp.json() else create_rsp.content
                )
                self.xray_folders_exist.append(case_repo)
            else:
                self.xray_folders_exist.append(case_repo)
        return True

    def __create_case(self, case_summary, case_description, case_repo, case_type, case_definition):
        graphql = """
        mutation {
            createTest(
                testType: { 
                    name: "%s" 
                },
                unstructured: "%s",
                folderPath: "%s",
                jira: {
                    fields: { 
                        summary: "%s", 
                        project: { 
                            key: "%s" 
                        },
                        description: "%s"
                    }
                }
            ) {
                test {
                    issueId
                    testType { name }
                    unstructured
                    jira(fields: ["key"])
                }
                warnings
            }
        }
        """ % (case_type, case_definition, case_repo, case_summary, self.jira_project_key, case_description)
        rsp = self.__xray_crud_case(request="createTest", graphql=graphql)
        return rsp["data"]["createTest"]["test"]

    def __get_xray_project_id(self):
        if self.jira_project_id is None:
            url = "{}/project/{}".format(self.jira_base_url, self.jira_project_key)
            self.total_rest_requests += 1
            rsp = self.session.get(url=url, headers=self.jira_headers, auth=(self.jira_user, self.jira_token))
            assert rsp.status_code == 200, "{} {}".format(rsp.status_code, rsp.json() if rsp.json() else rsp.content)
            self.jira_project_id = rsp.json().get("id")
        return self.jira_project_id

    def create_update_case(self, code_url, code_repo, code_path, code_lang, code_case):
        case_summary = code_path
        case_description = "\\n".join([
            self.case_description_prefix,
            code_url
        ])
        case_repo = "".join([
            self.xray_case_repo_home,
            code_repo
        ]) if str(code_repo).startswith("/") else "/".join([
            self.xray_case_repo_home,
            code_repo
        ])
        self.__check_create_case_folder(case_repo)
        case_type = "Generic"
        step_action = "\\n".join([
            "{quote}%s{quote}" % code_path,
            "{code:%s}%s{code}" % (
                code_lang, xray_test_code_dumps(code_case)
            )
        ])
        case_id = None
        for case_item in self.__search_case_by_summary(case_summary):
            case_id = case_item.get("issueId")
            issue_description = case_item["jira"].get("description")
            issue_description_is_changed = False if issue_description == case_description.replace("\\n", "\n") else True
            test_repo_path = case_item["folder"].get("path")
            test_repo_path_is_changed = False if test_repo_path == case_repo else True
            test_type = case_item["testType"].get("name")
            test_type_is_changed = False if test_type == case_type else True
            unstructured_content = case_item.get("unstructured")
            test_step_is_changed = False if unstructured_content == xray_test_code_loads(step_action) else True
            update_tag = False
            if issue_description_is_changed:
                self.app_logger.tab_warning("Update test case description")
                update_tag = True
                self.__update_case_description(case_id, code_url)
            if test_repo_path_is_changed:
                self.app_logger.tab_warning("Update test case folder")
                update_tag = True
                self.__update_case_folder(case_id, case_repo)
            if test_type_is_changed:
                self.app_logger.tab_warning("Update test case type")
                update_tag = True
                self.__update_case_type(case_id, case_type)
            if test_step_is_changed:
                self.app_logger.tab_warning("Update test case definition")
                update_tag = True
                self.__update_case_definition(case_id, step_action)
            if update_tag:
                self.total_update_cases += 1
            return True
        if case_id is None:
            self.app_logger.tab_warning("Create new test case")
            self.total_create_cases += 1
            return self.__create_case(case_summary, case_description, case_repo, case_type, step_action)


if __name__ == "__main__":
    print("🚀 This is an app script of XRAY")
