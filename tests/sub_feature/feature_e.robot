*** Settings ***
Documentation       TMAN Atlas AutoTestCase Manager Demo
Library             RequestsLibrary


*** Variables ***


*** Test Cases ***
Login App
    [Documentation]     Login Validation
    [Tags]              Demo
    Create Session      demo     https://en.tman.ltd
    ${rsp}     Get On Session    demo     /
    log    ${rsp.status_code}
    Should Be Equal     "${rsp.status_code}"    "200"
    log    login succeed

Logout App
    [Documentation]     Logout Validation
    [Tags]              Demo
    log    logout succeed


*** Keywords ***
