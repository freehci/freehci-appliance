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


class AdminUser(
    schemas.DictSchema
):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """


    class MetaOapg:
        
        class properties:
            name = schemas.StrSchema
            password = schemas.StrSchema
            userId = schemas.StrSchema
            enabled = schemas.BoolSchema
            
            
            class roles(
                schemas.ListSchema
            ):
            
            
                class MetaOapg:
                    
                    
                    class items(
                        schemas.EnumBase,
                        schemas.StrSchema
                    ):
                        
                        @schemas.classproperty
                        def ADMIN(cls):
                            return cls("ROLE_ADMIN")
                        
                        @schemas.classproperty
                        def MONITORING(cls):
                            return cls("ROLE_MONITORING")
            
                def __new__(
                    cls,
                    _arg: typing.Union[typing.Tuple[typing.Union[MetaOapg.items, str, ]], typing.List[typing.Union[MetaOapg.items, str, ]]],
                    _configuration: typing.Optional[schemas.Configuration] = None,
                ) -> 'roles':
                    return super().__new__(
                        cls,
                        _arg,
                        _configuration=_configuration,
                    )
            
                def __getitem__(self, i: int) -> MetaOapg.items:
                    return super().__getitem__(i)
            adminPasswordSetTime = schemas.StrSchema
            noOfDaysRemainingForPwdExpiry = schemas.Int32Schema
            
            
            class userType(
                schemas.EnumBase,
                schemas.StrSchema
            ):
                
                @schemas.classproperty
                def INTERNAL(cls):
                    return cls("INTERNAL")
                
                @schemas.classproperty
                def EXTERNAL(cls):
                    return cls("EXTERNAL")
            adminMonitoringPasswordPreExpired = schemas.BoolSchema
            __annotations__ = {
                "name": name,
                "password": password,
                "userId": userId,
                "enabled": enabled,
                "roles": roles,
                "adminPasswordSetTime": adminPasswordSetTime,
                "noOfDaysRemainingForPwdExpiry": noOfDaysRemainingForPwdExpiry,
                "userType": userType,
                "adminMonitoringPasswordPreExpired": adminMonitoringPasswordPreExpired,
            }
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["name"]) -> MetaOapg.properties.name: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["password"]) -> MetaOapg.properties.password: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["userId"]) -> MetaOapg.properties.userId: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["enabled"]) -> MetaOapg.properties.enabled: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["roles"]) -> MetaOapg.properties.roles: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["adminPasswordSetTime"]) -> MetaOapg.properties.adminPasswordSetTime: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["noOfDaysRemainingForPwdExpiry"]) -> MetaOapg.properties.noOfDaysRemainingForPwdExpiry: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["userType"]) -> MetaOapg.properties.userType: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["adminMonitoringPasswordPreExpired"]) -> MetaOapg.properties.adminMonitoringPasswordPreExpired: ...
    
    @typing.overload
    def __getitem__(self, name: str) -> schemas.UnsetAnyTypeSchema: ...
    
    def __getitem__(self, name: typing.Union[typing_extensions.Literal["name", "password", "userId", "enabled", "roles", "adminPasswordSetTime", "noOfDaysRemainingForPwdExpiry", "userType", "adminMonitoringPasswordPreExpired", ], str]):
        # dict_instance[name] accessor
        return super().__getitem__(name)
    
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["name"]) -> typing.Union[MetaOapg.properties.name, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["password"]) -> typing.Union[MetaOapg.properties.password, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["userId"]) -> typing.Union[MetaOapg.properties.userId, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["enabled"]) -> typing.Union[MetaOapg.properties.enabled, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["roles"]) -> typing.Union[MetaOapg.properties.roles, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["adminPasswordSetTime"]) -> typing.Union[MetaOapg.properties.adminPasswordSetTime, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["noOfDaysRemainingForPwdExpiry"]) -> typing.Union[MetaOapg.properties.noOfDaysRemainingForPwdExpiry, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["userType"]) -> typing.Union[MetaOapg.properties.userType, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["adminMonitoringPasswordPreExpired"]) -> typing.Union[MetaOapg.properties.adminMonitoringPasswordPreExpired, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: str) -> typing.Union[schemas.UnsetAnyTypeSchema, schemas.Unset]: ...
    
    def get_item_oapg(self, name: typing.Union[typing_extensions.Literal["name", "password", "userId", "enabled", "roles", "adminPasswordSetTime", "noOfDaysRemainingForPwdExpiry", "userType", "adminMonitoringPasswordPreExpired", ], str]):
        return super().get_item_oapg(name)
    

    def __new__(
        cls,
        *_args: typing.Union[dict, frozendict.frozendict, ],
        name: typing.Union[MetaOapg.properties.name, str, schemas.Unset] = schemas.unset,
        password: typing.Union[MetaOapg.properties.password, str, schemas.Unset] = schemas.unset,
        userId: typing.Union[MetaOapg.properties.userId, str, schemas.Unset] = schemas.unset,
        enabled: typing.Union[MetaOapg.properties.enabled, bool, schemas.Unset] = schemas.unset,
        roles: typing.Union[MetaOapg.properties.roles, list, tuple, schemas.Unset] = schemas.unset,
        adminPasswordSetTime: typing.Union[MetaOapg.properties.adminPasswordSetTime, str, schemas.Unset] = schemas.unset,
        noOfDaysRemainingForPwdExpiry: typing.Union[MetaOapg.properties.noOfDaysRemainingForPwdExpiry, decimal.Decimal, int, schemas.Unset] = schemas.unset,
        userType: typing.Union[MetaOapg.properties.userType, str, schemas.Unset] = schemas.unset,
        adminMonitoringPasswordPreExpired: typing.Union[MetaOapg.properties.adminMonitoringPasswordPreExpired, bool, schemas.Unset] = schemas.unset,
        _configuration: typing.Optional[schemas.Configuration] = None,
        **kwargs: typing.Union[schemas.AnyTypeSchema, dict, frozendict.frozendict, str, date, datetime, uuid.UUID, int, float, decimal.Decimal, None, list, tuple, bytes],
    ) -> 'AdminUser':
        return super().__new__(
            cls,
            *_args,
            name=name,
            password=password,
            userId=userId,
            enabled=enabled,
            roles=roles,
            adminPasswordSetTime=adminPasswordSetTime,
            noOfDaysRemainingForPwdExpiry=noOfDaysRemainingForPwdExpiry,
            userType=userType,
            adminMonitoringPasswordPreExpired=adminMonitoringPasswordPreExpired,
            _configuration=_configuration,
            **kwargs,
        )
