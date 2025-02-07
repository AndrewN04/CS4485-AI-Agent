"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
*!
Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022-2025)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import builtins
import collections.abc
import google.protobuf.descriptor
import google.protobuf.internal.containers
import google.protobuf.message
import streamlit.proto.PageProfile_pb2
import typing

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor

@typing.final
class MetricsEvent(google.protobuf.message.Message):
    """Metrics events:"""

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    EVENT_FIELD_NUMBER: builtins.int
    ANONYMOUS_ID_FIELD_NUMBER: builtins.int
    MACHINE_ID_V3_FIELD_NUMBER: builtins.int
    REPORT_HASH_FIELD_NUMBER: builtins.int
    DEV_FIELD_NUMBER: builtins.int
    SOURCE_FIELD_NUMBER: builtins.int
    STREAMLIT_VERSION_FIELD_NUMBER: builtins.int
    IS_HELLO_FIELD_NUMBER: builtins.int
    HOSTED_AT_FIELD_NUMBER: builtins.int
    OWNER_FIELD_NUMBER: builtins.int
    REPO_FIELD_NUMBER: builtins.int
    BRANCH_FIELD_NUMBER: builtins.int
    MAIN_MODULE_FIELD_NUMBER: builtins.int
    CREATOR_ID_FIELD_NUMBER: builtins.int
    CONTEXT_PAGE_URL_FIELD_NUMBER: builtins.int
    CONTEXT_PAGE_TITLE_FIELD_NUMBER: builtins.int
    CONTEXT_PAGE_PATH_FIELD_NUMBER: builtins.int
    CONTEXT_PAGE_REFERRER_FIELD_NUMBER: builtins.int
    CONTEXT_PAGE_SEARCH_FIELD_NUMBER: builtins.int
    CONTEXT_LOCALE_FIELD_NUMBER: builtins.int
    CONTEXT_USER_AGENT_FIELD_NUMBER: builtins.int
    LABEL_FIELD_NUMBER: builtins.int
    COMMANDS_FIELD_NUMBER: builtins.int
    EXEC_TIME_FIELD_NUMBER: builtins.int
    PREP_TIME_FIELD_NUMBER: builtins.int
    CONFIG_FIELD_NUMBER: builtins.int
    UNCAUGHT_EXCEPTION_FIELD_NUMBER: builtins.int
    ATTRIBUTIONS_FIELD_NUMBER: builtins.int
    OS_FIELD_NUMBER: builtins.int
    TIMEZONE_FIELD_NUMBER: builtins.int
    HEADLESS_FIELD_NUMBER: builtins.int
    IS_FRAGMENT_RUN_FIELD_NUMBER: builtins.int
    APP_ID_FIELD_NUMBER: builtins.int
    NUMPAGES_FIELD_NUMBER: builtins.int
    SESSION_ID_FIELD_NUMBER: builtins.int
    PYTHON_VERSION_FIELD_NUMBER: builtins.int
    PAGE_SCRIPT_HASH_FIELD_NUMBER: builtins.int
    ACTIVE_THEME_FIELD_NUMBER: builtins.int
    TOTAL_LOAD_TIME_FIELD_NUMBER: builtins.int
    BROWSER_INFO_FIELD_NUMBER: builtins.int
    event: builtins.str
    """Common Event Fields:"""
    anonymous_id: builtins.str
    machine_id_v3: builtins.str
    report_hash: builtins.str
    dev: builtins.bool
    source: builtins.str
    streamlit_version: builtins.str
    is_hello: builtins.bool
    hosted_at: builtins.str
    """Host tracking fields:"""
    owner: builtins.str
    repo: builtins.str
    branch: builtins.str
    main_module: builtins.str
    creator_id: builtins.str
    context_page_url: builtins.str
    """Context fields:"""
    context_page_title: builtins.str
    context_page_path: builtins.str
    context_page_referrer: builtins.str
    context_page_search: builtins.str
    context_locale: builtins.str
    context_user_agent: builtins.str
    label: builtins.str
    """Menu Click Event field:"""
    exec_time: builtins.int
    prep_time: builtins.int
    uncaught_exception: builtins.str
    os: builtins.str
    timezone: builtins.str
    headless: builtins.bool
    is_fragment_run: builtins.bool
    app_id: builtins.str
    """Addtl for page profile metrics"""
    numPages: builtins.int
    session_id: builtins.str
    python_version: builtins.str
    page_script_hash: builtins.str
    active_theme: builtins.str
    total_load_time: builtins.int
    @property
    def commands(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[streamlit.proto.PageProfile_pb2.Command]:
        """Page Profile Event fields:
        Same as PageProfile msg
        """

    @property
    def config(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[builtins.str]: ...
    @property
    def attributions(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[builtins.str]: ...
    @property
    def browser_info(self) -> global___BrowserInfo: ...
    def __init__(
        self,
        *,
        event: builtins.str = ...,
        anonymous_id: builtins.str = ...,
        machine_id_v3: builtins.str = ...,
        report_hash: builtins.str = ...,
        dev: builtins.bool = ...,
        source: builtins.str = ...,
        streamlit_version: builtins.str = ...,
        is_hello: builtins.bool = ...,
        hosted_at: builtins.str = ...,
        owner: builtins.str = ...,
        repo: builtins.str = ...,
        branch: builtins.str = ...,
        main_module: builtins.str = ...,
        creator_id: builtins.str = ...,
        context_page_url: builtins.str = ...,
        context_page_title: builtins.str = ...,
        context_page_path: builtins.str = ...,
        context_page_referrer: builtins.str = ...,
        context_page_search: builtins.str = ...,
        context_locale: builtins.str = ...,
        context_user_agent: builtins.str = ...,
        label: builtins.str = ...,
        commands: collections.abc.Iterable[streamlit.proto.PageProfile_pb2.Command] | None = ...,
        exec_time: builtins.int = ...,
        prep_time: builtins.int = ...,
        config: collections.abc.Iterable[builtins.str] | None = ...,
        uncaught_exception: builtins.str = ...,
        attributions: collections.abc.Iterable[builtins.str] | None = ...,
        os: builtins.str = ...,
        timezone: builtins.str = ...,
        headless: builtins.bool = ...,
        is_fragment_run: builtins.bool = ...,
        app_id: builtins.str = ...,
        numPages: builtins.int = ...,
        session_id: builtins.str = ...,
        python_version: builtins.str = ...,
        page_script_hash: builtins.str = ...,
        active_theme: builtins.str = ...,
        total_load_time: builtins.int = ...,
        browser_info: global___BrowserInfo | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing.Literal["browser_info", b"browser_info"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing.Literal["active_theme", b"active_theme", "anonymous_id", b"anonymous_id", "app_id", b"app_id", "attributions", b"attributions", "branch", b"branch", "browser_info", b"browser_info", "commands", b"commands", "config", b"config", "context_locale", b"context_locale", "context_page_path", b"context_page_path", "context_page_referrer", b"context_page_referrer", "context_page_search", b"context_page_search", "context_page_title", b"context_page_title", "context_page_url", b"context_page_url", "context_user_agent", b"context_user_agent", "creator_id", b"creator_id", "dev", b"dev", "event", b"event", "exec_time", b"exec_time", "headless", b"headless", "hosted_at", b"hosted_at", "is_fragment_run", b"is_fragment_run", "is_hello", b"is_hello", "label", b"label", "machine_id_v3", b"machine_id_v3", "main_module", b"main_module", "numPages", b"numPages", "os", b"os", "owner", b"owner", "page_script_hash", b"page_script_hash", "prep_time", b"prep_time", "python_version", b"python_version", "repo", b"repo", "report_hash", b"report_hash", "session_id", b"session_id", "source", b"source", "streamlit_version", b"streamlit_version", "timezone", b"timezone", "total_load_time", b"total_load_time", "uncaught_exception", b"uncaught_exception"]) -> None: ...

global___MetricsEvent = MetricsEvent

@typing.final
class BrowserInfo(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    BROWSER_NAME_FIELD_NUMBER: builtins.int
    BROWSER_VERSION_FIELD_NUMBER: builtins.int
    DEVICE_TYPE_FIELD_NUMBER: builtins.int
    OS_FIELD_NUMBER: builtins.int
    browser_name: builtins.str
    browser_version: builtins.str
    device_type: builtins.str
    os: builtins.str
    def __init__(
        self,
        *,
        browser_name: builtins.str = ...,
        browser_version: builtins.str = ...,
        device_type: builtins.str = ...,
        os: builtins.str = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing.Literal["browser_name", b"browser_name", "browser_version", b"browser_version", "device_type", b"device_type", "os", b"os"]) -> None: ...

global___BrowserInfo = BrowserInfo
