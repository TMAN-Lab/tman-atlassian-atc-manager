#!/usr/bin/env python3

import requests


class Test(object):
    def setup(self):
        pass

    def teardown(self):
        pass

    def test_login(self):
        session = requests.session()
        rsp = session.get("https://en.tman.ltd")
        assert rsp.status_code == 200

    def test_list_object(self):
        print("Test Case: list object")
        assert True

    def test_head_object(self):
        print("Test Case: head object")
        assert True

    def test_post_object(self):
        print("Test Case: post object")
        assert False

    def test_put_object(self):
        print("Test Case: put object")
        assert False
        assert True

    def test_get_object(self):
        print("Test Case: get object")
        assert True

    def test_delete_object(self):
        print("Test Case: delete object")
        assert False

    def test_get_permission(self):
        print("Test Case: get permission")
        assert True

    def test_post_permission(self):
        print("Test Case: post permission")
        assert False

    def test_logout(self):
        print("Test Case: logout")
        assert True


if __name__ == "__main__":
    print("This is pytest test case")
