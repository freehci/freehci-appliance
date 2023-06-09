# coding: utf-8

"""
    Unified Access Gateway REST API

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 1.0.2
    Generated by: https://openapi-generator.tech
"""

from datetime import date, datetime  # noqa: F401
import decimal  # noqa: F401
import functools  # noqa: F401
import io  # noqa: F401
import re  # noqa: F401
import typing  # noqa: F401
import typing_extensions  # noqa: F401
import uuid  # noqa: F401

import frozendict  # noqa: F401

from openapi_client import schemas  # noqa: F401


class SyslogServerSettings(
    schemas.DictSchema
):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """


    class MetaOapg:
        
        class properties:
            syslogCategory = schemas.StrSchema
            
            
            class syslogCategoryList(
                schemas.ListSchema
            ):
            
            
                class MetaOapg:
                    
                    
                    class items(
                        schemas.EnumBase,
                        schemas.StrSchema
                    ):
                    
                    
                        class MetaOapg:
                            enum_value_to_name = {
                                "ALL": "ALL",
                                "AUDIT": "AUDIT",
                                "APPLICATION": "APPLICATION",
                                "SYSTEM": "SYSTEM",
                                "TRACEABILITY": "TRACEABILITY",
                                "STATS": "STATS",
                                "DEPLOYMENT": "DEPLOYMENT",
                            }
                        
                        @schemas.classproperty
                        def ALL(cls):
                            return cls("ALL")
                        
                        @schemas.classproperty
                        def AUDIT(cls):
                            return cls("AUDIT")
                        
                        @schemas.classproperty
                        def APPLICATION(cls):
                            return cls("APPLICATION")
                        
                        @schemas.classproperty
                        def SYSTEM(cls):
                            return cls("SYSTEM")
                        
                        @schemas.classproperty
                        def TRACEABILITY(cls):
                            return cls("TRACEABILITY")
                        
                        @schemas.classproperty
                        def STATS(cls):
                            return cls("STATS")
                        
                        @schemas.classproperty
                        def DEPLOYMENT(cls):
                            return cls("DEPLOYMENT")
            
                def __new__(
                    cls,
                    _arg: typing.Union[typing.Tuple[typing.Union[MetaOapg.items, str, ]], typing.List[typing.Union[MetaOapg.items, str, ]]],
                    _configuration: typing.Optional[schemas.Configuration] = None,
                ) -> 'syslogCategoryList':
                    return super().__new__(
                        cls,
                        _arg,
                        _configuration=_configuration,
                    )
            
                def __getitem__(self, i: int) -> MetaOapg.items:
                    return super().__getitem__(i)
            
            
            class syslogFormat(
                schemas.EnumBase,
                schemas.StrSchema
            ):
            
            
                class MetaOapg:
                    enum_value_to_name = {
                        "TEXT": "TEXT",
                        "JSON_TITAN": "JSON_TITAN",
                        "JSON_EXPANDED": "JSON_EXPANDED",
                    }
                
                @schemas.classproperty
                def TEXT(cls):
                    return cls("TEXT")
                
                @schemas.classproperty
                def JSON_TITAN(cls):
                    return cls("JSON_TITAN")
                
                @schemas.classproperty
                def JSON_EXPANDED(cls):
                    return cls("JSON_EXPANDED")
            
            
            class sysLogType(
                schemas.EnumBase,
                schemas.StrSchema
            ):
            
            
                class MetaOapg:
                    enum_value_to_name = {
                        "UDP": "UDP",
                        "TCP": "TCP",
                        "TLS": "TLS",
                        "MQTT": "MQTT",
                    }
                
                @schemas.classproperty
                def UDP(cls):
                    return cls("UDP")
                
                @schemas.classproperty
                def TCP(cls):
                    return cls("TCP")
                
                @schemas.classproperty
                def TLS(cls):
                    return cls("TLS")
                
                @schemas.classproperty
                def MQTT(cls):
                    return cls("MQTT")
            syslogSystemMessagesEnabledV2 = schemas.BoolSchema
            syslogUrl = schemas.StrSchema
            mqttTopic = schemas.StrSchema
            
            
            class syslogSettingName(
                schemas.StrSchema
            ):
            
            
                class MetaOapg:
                    regex=[{
                        'pattern': r'^[a-zA-Z\d_-]{2,50}$',  # noqa: E501
                    }]
        
            @staticmethod
            def tlsSyslogServerSettings() -> typing.Type['TlsSyslogServerSettings']:
                return TlsSyslogServerSettings
        
            @staticmethod
            def tlsMqttServerSettings() -> typing.Type['TlsMqttServerSettings']:
                return TlsMqttServerSettings
            __annotations__ = {
                "syslogCategory": syslogCategory,
                "syslogCategoryList": syslogCategoryList,
                "syslogFormat": syslogFormat,
                "sysLogType": sysLogType,
                "syslogSystemMessagesEnabledV2": syslogSystemMessagesEnabledV2,
                "syslogUrl": syslogUrl,
                "mqttTopic": mqttTopic,
                "syslogSettingName": syslogSettingName,
                "tlsSyslogServerSettings": tlsSyslogServerSettings,
                "tlsMqttServerSettings": tlsMqttServerSettings,
            }
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["syslogCategory"]) -> MetaOapg.properties.syslogCategory: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["syslogCategoryList"]) -> MetaOapg.properties.syslogCategoryList: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["syslogFormat"]) -> MetaOapg.properties.syslogFormat: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["sysLogType"]) -> MetaOapg.properties.sysLogType: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["syslogSystemMessagesEnabledV2"]) -> MetaOapg.properties.syslogSystemMessagesEnabledV2: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["syslogUrl"]) -> MetaOapg.properties.syslogUrl: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["mqttTopic"]) -> MetaOapg.properties.mqttTopic: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["syslogSettingName"]) -> MetaOapg.properties.syslogSettingName: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["tlsSyslogServerSettings"]) -> 'TlsSyslogServerSettings': ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["tlsMqttServerSettings"]) -> 'TlsMqttServerSettings': ...
    
    @typing.overload
    def __getitem__(self, name: str) -> schemas.UnsetAnyTypeSchema: ...
    
    def __getitem__(self, name: typing.Union[typing_extensions.Literal["syslogCategory", "syslogCategoryList", "syslogFormat", "sysLogType", "syslogSystemMessagesEnabledV2", "syslogUrl", "mqttTopic", "syslogSettingName", "tlsSyslogServerSettings", "tlsMqttServerSettings", ], str]):
        # dict_instance[name] accessor
        return super().__getitem__(name)
    
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["syslogCategory"]) -> typing.Union[MetaOapg.properties.syslogCategory, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["syslogCategoryList"]) -> typing.Union[MetaOapg.properties.syslogCategoryList, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["syslogFormat"]) -> typing.Union[MetaOapg.properties.syslogFormat, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["sysLogType"]) -> typing.Union[MetaOapg.properties.sysLogType, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["syslogSystemMessagesEnabledV2"]) -> typing.Union[MetaOapg.properties.syslogSystemMessagesEnabledV2, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["syslogUrl"]) -> typing.Union[MetaOapg.properties.syslogUrl, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["mqttTopic"]) -> typing.Union[MetaOapg.properties.mqttTopic, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["syslogSettingName"]) -> typing.Union[MetaOapg.properties.syslogSettingName, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["tlsSyslogServerSettings"]) -> typing.Union['TlsSyslogServerSettings', schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["tlsMqttServerSettings"]) -> typing.Union['TlsMqttServerSettings', schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: str) -> typing.Union[schemas.UnsetAnyTypeSchema, schemas.Unset]: ...
    
    def get_item_oapg(self, name: typing.Union[typing_extensions.Literal["syslogCategory", "syslogCategoryList", "syslogFormat", "sysLogType", "syslogSystemMessagesEnabledV2", "syslogUrl", "mqttTopic", "syslogSettingName", "tlsSyslogServerSettings", "tlsMqttServerSettings", ], str]):
        return super().get_item_oapg(name)
    

    def __new__(
        cls,
        *_args: typing.Union[dict, frozendict.frozendict, ],
        syslogCategory: typing.Union[MetaOapg.properties.syslogCategory, str, schemas.Unset] = schemas.unset,
        syslogCategoryList: typing.Union[MetaOapg.properties.syslogCategoryList, list, tuple, schemas.Unset] = schemas.unset,
        syslogFormat: typing.Union[MetaOapg.properties.syslogFormat, str, schemas.Unset] = schemas.unset,
        sysLogType: typing.Union[MetaOapg.properties.sysLogType, str, schemas.Unset] = schemas.unset,
        syslogSystemMessagesEnabledV2: typing.Union[MetaOapg.properties.syslogSystemMessagesEnabledV2, bool, schemas.Unset] = schemas.unset,
        syslogUrl: typing.Union[MetaOapg.properties.syslogUrl, str, schemas.Unset] = schemas.unset,
        mqttTopic: typing.Union[MetaOapg.properties.mqttTopic, str, schemas.Unset] = schemas.unset,
        syslogSettingName: typing.Union[MetaOapg.properties.syslogSettingName, str, schemas.Unset] = schemas.unset,
        tlsSyslogServerSettings: typing.Union['TlsSyslogServerSettings', schemas.Unset] = schemas.unset,
        tlsMqttServerSettings: typing.Union['TlsMqttServerSettings', schemas.Unset] = schemas.unset,
        _configuration: typing.Optional[schemas.Configuration] = None,
        **kwargs: typing.Union[schemas.AnyTypeSchema, dict, frozendict.frozendict, str, date, datetime, uuid.UUID, int, float, decimal.Decimal, None, list, tuple, bytes],
    ) -> 'SyslogServerSettings':
        return super().__new__(
            cls,
            *_args,
            syslogCategory=syslogCategory,
            syslogCategoryList=syslogCategoryList,
            syslogFormat=syslogFormat,
            sysLogType=sysLogType,
            syslogSystemMessagesEnabledV2=syslogSystemMessagesEnabledV2,
            syslogUrl=syslogUrl,
            mqttTopic=mqttTopic,
            syslogSettingName=syslogSettingName,
            tlsSyslogServerSettings=tlsSyslogServerSettings,
            tlsMqttServerSettings=tlsMqttServerSettings,
            _configuration=_configuration,
            **kwargs,
        )

from openapi_client.model.tls_mqtt_server_settings import TlsMqttServerSettings
from openapi_client.model.tls_syslog_server_settings import TlsSyslogServerSettings
