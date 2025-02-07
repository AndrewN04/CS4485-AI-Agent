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
import google.protobuf.internal.enum_type_wrapper
import google.protobuf.message
import streamlit.proto.AuthRedirect_pb2
import streamlit.proto.AutoRerun_pb2
import streamlit.proto.Common_pb2
import streamlit.proto.Delta_pb2
import streamlit.proto.GitInfo_pb2
import streamlit.proto.Logo_pb2
import streamlit.proto.Navigation_pb2
import streamlit.proto.NewSession_pb2
import streamlit.proto.PageConfig_pb2
import streamlit.proto.PageInfo_pb2
import streamlit.proto.PageNotFound_pb2
import streamlit.proto.PageProfile_pb2
import streamlit.proto.PagesChanged_pb2
import streamlit.proto.ParentMessage_pb2
import streamlit.proto.SessionEvent_pb2
import streamlit.proto.SessionStatus_pb2
import sys
import typing

if sys.version_info >= (3, 10):
    import typing as typing_extensions
else:
    import typing_extensions

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor

@typing.final
class ForwardMsg(google.protobuf.message.Message):
    """A message sent from Proxy to the browser"""

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    class _ScriptFinishedStatus:
        ValueType = typing.NewType("ValueType", builtins.int)
        V: typing_extensions.TypeAlias = ValueType

    class _ScriptFinishedStatusEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[ForwardMsg._ScriptFinishedStatus.ValueType], builtins.type):
        DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
        FINISHED_SUCCESSFULLY: ForwardMsg._ScriptFinishedStatus.ValueType  # 0
        """The script compiled and ran."""
        FINISHED_WITH_COMPILE_ERROR: ForwardMsg._ScriptFinishedStatus.ValueType  # 1
        """The script failed to compile"""
        FINISHED_EARLY_FOR_RERUN: ForwardMsg._ScriptFinishedStatus.ValueType  # 2
        """Script was interrupted by rerun"""
        FINISHED_FRAGMENT_RUN_SUCCESSFULLY: ForwardMsg._ScriptFinishedStatus.ValueType  # 3
        """A fragment of the script ran successfully."""

    class ScriptFinishedStatus(_ScriptFinishedStatus, metaclass=_ScriptFinishedStatusEnumTypeWrapper):
        """Values for the 'script_finished` type"""

    FINISHED_SUCCESSFULLY: ForwardMsg.ScriptFinishedStatus.ValueType  # 0
    """The script compiled and ran."""
    FINISHED_WITH_COMPILE_ERROR: ForwardMsg.ScriptFinishedStatus.ValueType  # 1
    """The script failed to compile"""
    FINISHED_EARLY_FOR_RERUN: ForwardMsg.ScriptFinishedStatus.ValueType  # 2
    """Script was interrupted by rerun"""
    FINISHED_FRAGMENT_RUN_SUCCESSFULLY: ForwardMsg.ScriptFinishedStatus.ValueType  # 3
    """A fragment of the script ran successfully."""

    HASH_FIELD_NUMBER: builtins.int
    METADATA_FIELD_NUMBER: builtins.int
    NEW_SESSION_FIELD_NUMBER: builtins.int
    DELTA_FIELD_NUMBER: builtins.int
    PAGE_INFO_CHANGED_FIELD_NUMBER: builtins.int
    PAGE_CONFIG_CHANGED_FIELD_NUMBER: builtins.int
    SCRIPT_FINISHED_FIELD_NUMBER: builtins.int
    GIT_INFO_CHANGED_FIELD_NUMBER: builtins.int
    PAGE_PROFILE_FIELD_NUMBER: builtins.int
    SESSION_STATUS_CHANGED_FIELD_NUMBER: builtins.int
    SESSION_EVENT_FIELD_NUMBER: builtins.int
    NAVIGATION_FIELD_NUMBER: builtins.int
    PAGE_NOT_FOUND_FIELD_NUMBER: builtins.int
    PAGES_CHANGED_FIELD_NUMBER: builtins.int
    FILE_URLS_RESPONSE_FIELD_NUMBER: builtins.int
    AUTO_RERUN_FIELD_NUMBER: builtins.int
    LOGO_FIELD_NUMBER: builtins.int
    AUTH_REDIRECT_FIELD_NUMBER: builtins.int
    PARENT_MESSAGE_FIELD_NUMBER: builtins.int
    REF_HASH_FIELD_NUMBER: builtins.int
    DEBUG_LAST_BACKMSG_ID_FIELD_NUMBER: builtins.int
    hash: builtins.str
    """A hash that uniquely identifies this ForwardMsg, for caching."""
    script_finished: global___ForwardMsg.ScriptFinishedStatus.ValueType
    ref_hash: builtins.str
    """A reference to a ForwardMsg that has already been delivered.
    The client should substitute the message with the given hash
    for this one. If the client does not have the referenced message
    in its cache, it can retrieve it from the server.
    """
    debug_last_backmsg_id: builtins.str
    """The ID of the last BackMsg that we received before sending this
    ForwardMsg. As its name suggests, this field should only be used for
    testing.
    """
    @property
    def metadata(self) -> global___ForwardMsgMetadata:
        """Contains 'non-payload' ForwardMsg data that isn't cached for the purposes
        of ForwardMsg de-duping.
        """

    @property
    def new_session(self) -> streamlit.proto.NewSession_pb2.NewSession:
        """App lifecycle messages."""

    @property
    def delta(self) -> streamlit.proto.Delta_pb2.Delta: ...
    @property
    def page_info_changed(self) -> streamlit.proto.PageInfo_pb2.PageInfo: ...
    @property
    def page_config_changed(self) -> streamlit.proto.PageConfig_pb2.PageConfig: ...
    @property
    def git_info_changed(self) -> streamlit.proto.GitInfo_pb2.GitInfo: ...
    @property
    def page_profile(self) -> streamlit.proto.PageProfile_pb2.PageProfile: ...
    @property
    def session_status_changed(self) -> streamlit.proto.SessionStatus_pb2.SessionStatus:
        """Status change and event messages."""

    @property
    def session_event(self) -> streamlit.proto.SessionEvent_pb2.SessionEvent: ...
    @property
    def navigation(self) -> streamlit.proto.Navigation_pb2.Navigation:
        """Other messages."""

    @property
    def page_not_found(self) -> streamlit.proto.PageNotFound_pb2.PageNotFound: ...
    @property
    def pages_changed(self) -> streamlit.proto.PagesChanged_pb2.PagesChanged: ...
    @property
    def file_urls_response(self) -> streamlit.proto.Common_pb2.FileURLsResponse: ...
    @property
    def auto_rerun(self) -> streamlit.proto.AutoRerun_pb2.AutoRerun: ...
    @property
    def logo(self) -> streamlit.proto.Logo_pb2.Logo:
        """App logo message"""

    @property
    def auth_redirect(self) -> streamlit.proto.AuthRedirect_pb2.AuthRedirect:
        """Auth redirect message"""

    @property
    def parent_message(self) -> streamlit.proto.ParentMessage_pb2.ParentMessage:
        """Platform - message to host"""

    def __init__(
        self,
        *,
        hash: builtins.str = ...,
        metadata: global___ForwardMsgMetadata | None = ...,
        new_session: streamlit.proto.NewSession_pb2.NewSession | None = ...,
        delta: streamlit.proto.Delta_pb2.Delta | None = ...,
        page_info_changed: streamlit.proto.PageInfo_pb2.PageInfo | None = ...,
        page_config_changed: streamlit.proto.PageConfig_pb2.PageConfig | None = ...,
        script_finished: global___ForwardMsg.ScriptFinishedStatus.ValueType = ...,
        git_info_changed: streamlit.proto.GitInfo_pb2.GitInfo | None = ...,
        page_profile: streamlit.proto.PageProfile_pb2.PageProfile | None = ...,
        session_status_changed: streamlit.proto.SessionStatus_pb2.SessionStatus | None = ...,
        session_event: streamlit.proto.SessionEvent_pb2.SessionEvent | None = ...,
        navigation: streamlit.proto.Navigation_pb2.Navigation | None = ...,
        page_not_found: streamlit.proto.PageNotFound_pb2.PageNotFound | None = ...,
        pages_changed: streamlit.proto.PagesChanged_pb2.PagesChanged | None = ...,
        file_urls_response: streamlit.proto.Common_pb2.FileURLsResponse | None = ...,
        auto_rerun: streamlit.proto.AutoRerun_pb2.AutoRerun | None = ...,
        logo: streamlit.proto.Logo_pb2.Logo | None = ...,
        auth_redirect: streamlit.proto.AuthRedirect_pb2.AuthRedirect | None = ...,
        parent_message: streamlit.proto.ParentMessage_pb2.ParentMessage | None = ...,
        ref_hash: builtins.str = ...,
        debug_last_backmsg_id: builtins.str = ...,
    ) -> None: ...
    def HasField(self, field_name: typing.Literal["auth_redirect", b"auth_redirect", "auto_rerun", b"auto_rerun", "delta", b"delta", "file_urls_response", b"file_urls_response", "git_info_changed", b"git_info_changed", "logo", b"logo", "metadata", b"metadata", "navigation", b"navigation", "new_session", b"new_session", "page_config_changed", b"page_config_changed", "page_info_changed", b"page_info_changed", "page_not_found", b"page_not_found", "page_profile", b"page_profile", "pages_changed", b"pages_changed", "parent_message", b"parent_message", "ref_hash", b"ref_hash", "script_finished", b"script_finished", "session_event", b"session_event", "session_status_changed", b"session_status_changed", "type", b"type"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing.Literal["auth_redirect", b"auth_redirect", "auto_rerun", b"auto_rerun", "debug_last_backmsg_id", b"debug_last_backmsg_id", "delta", b"delta", "file_urls_response", b"file_urls_response", "git_info_changed", b"git_info_changed", "hash", b"hash", "logo", b"logo", "metadata", b"metadata", "navigation", b"navigation", "new_session", b"new_session", "page_config_changed", b"page_config_changed", "page_info_changed", b"page_info_changed", "page_not_found", b"page_not_found", "page_profile", b"page_profile", "pages_changed", b"pages_changed", "parent_message", b"parent_message", "ref_hash", b"ref_hash", "script_finished", b"script_finished", "session_event", b"session_event", "session_status_changed", b"session_status_changed", "type", b"type"]) -> None: ...
    def WhichOneof(self, oneof_group: typing.Literal["type", b"type"]) -> typing.Literal["new_session", "delta", "page_info_changed", "page_config_changed", "script_finished", "git_info_changed", "page_profile", "session_status_changed", "session_event", "navigation", "page_not_found", "pages_changed", "file_urls_response", "auto_rerun", "logo", "auth_redirect", "parent_message", "ref_hash"] | None: ...

global___ForwardMsg = ForwardMsg

@typing.final
class ForwardMsgMetadata(google.protobuf.message.Message):
    """ForwardMsgMetadata contains all data that does _not_ get hashed (or cached)
    in our ForwardMsgCache. (That is, when we cache a ForwardMsg, we clear its
    metadata field first.) This allows us to, e.g., have a large unchanging
    dataframe appear in different places across multiple reruns - or even appear
    multiple times in a single run - and only send its dataframe bytes once.
    """

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    CACHEABLE_FIELD_NUMBER: builtins.int
    DELTA_PATH_FIELD_NUMBER: builtins.int
    ELEMENT_DIMENSION_SPEC_FIELD_NUMBER: builtins.int
    ACTIVE_SCRIPT_HASH_FIELD_NUMBER: builtins.int
    cacheable: builtins.bool
    """If this is set, the server will have cached this message,
    and a client that receives it should do the same.
    """
    active_script_hash: builtins.str
    """active_script_hash the forward message is associated from.
    For multipage apps v1, this will always be the page file running
    For multipage apps v2, this can be the main script or the page script
    """
    @property
    def delta_path(self) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[builtins.int]:
        """The path that identifies a delta's location in the report tree.
        Only set for Delta messages.
        """

    @property
    def element_dimension_spec(self) -> global___ElementDimensionSpec:
        """DEPRECATED: This is not used anymore."""

    def __init__(
        self,
        *,
        cacheable: builtins.bool = ...,
        delta_path: collections.abc.Iterable[builtins.int] | None = ...,
        element_dimension_spec: global___ElementDimensionSpec | None = ...,
        active_script_hash: builtins.str = ...,
    ) -> None: ...
    def HasField(self, field_name: typing.Literal["element_dimension_spec", b"element_dimension_spec"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing.Literal["active_script_hash", b"active_script_hash", "cacheable", b"cacheable", "delta_path", b"delta_path", "element_dimension_spec", b"element_dimension_spec"]) -> None: ...

global___ForwardMsgMetadata = ForwardMsgMetadata

@typing.final
class ElementDimensionSpec(google.protobuf.message.Message):
    """DEPRECATED: This is not used anymore.
    Specifies the dimensions for the element
    """

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    WIDTH_FIELD_NUMBER: builtins.int
    HEIGHT_FIELD_NUMBER: builtins.int
    width: builtins.int
    """width in pixels"""
    height: builtins.int
    """height in pixels"""
    def __init__(
        self,
        *,
        width: builtins.int = ...,
        height: builtins.int = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing.Literal["height", b"height", "width", b"width"]) -> None: ...

global___ElementDimensionSpec = ElementDimensionSpec

@typing.final
class ForwardMsgList(google.protobuf.message.Message):
    """This is a list of ForwardMessages used to have a single protobuf message
    that encapsulates multiple ForwardMessages. This is used in static streamlit app
    generation in replaying all of the protobuf messages of a streamlit app. The
    ForwardMsgList allows us to leverage the built-ins of protobuf in delimiting the ForwardMsgs
    instead of needing to do that ourselves.
    """

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    MESSAGES_FIELD_NUMBER: builtins.int
    @property
    def messages(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___ForwardMsg]: ...
    def __init__(
        self,
        *,
        messages: collections.abc.Iterable[global___ForwardMsg] | None = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing.Literal["messages", b"messages"]) -> None: ...

global___ForwardMsgList = ForwardMsgList
