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


class OpswatDevicePolicySettings(
    schemas.ComposedSchema,
):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """


    class MetaOapg:
        
        
        class all_of_1(
            schemas.DictSchema
        ):
        
        
            class MetaOapg:
                required = {
                    "password",
                    "userName",
                }
                
                class properties:
                    
                    
                    class allowedStatuses(
                        schemas.ListSchema
                    ):
                    
                    
                        class MetaOapg:
                            
                            
                            class items(
                                schemas.EnumBase,
                                schemas.StrSchema
                            ):
                                
                                @schemas.classproperty
                                def COMPLIANT(cls):
                                    return cls("COMPLIANT")
                                
                                @schemas.classproperty
                                def NON_COMPLIANT(cls):
                                    return cls("NON_COMPLIANT")
                                
                                @schemas.classproperty
                                def OUT_OF_LICENSE_USAGE(cls):
                                    return cls("OUT_OF_LICENSE_USAGE")
                                
                                @schemas.classproperty
                                def NOT_FOUND(cls):
                                    return cls("NOT_FOUND")
                                
                                @schemas.classproperty
                                def ASSESSMENT_PENDING(cls):
                                    return cls("ASSESSMENT_PENDING")
                                
                                @schemas.classproperty
                                def OTHERS(cls):
                                    return cls("OTHERS")
                    
                        def __new__(
                            cls,
                            _arg: typing.Union[typing.Tuple[typing.Union[MetaOapg.items, str, ]], typing.List[typing.Union[MetaOapg.items, str, ]]],
                            _configuration: typing.Optional[schemas.Configuration] = None,
                        ) -> 'allowedStatuses':
                            return super().__new__(
                                cls,
                                _arg,
                                _configuration=_configuration,
                            )
                    
                        def __getitem__(self, i: int) -> MetaOapg.items:
                            return super().__getitem__(i)
                    userName = schemas.StrSchema
                    password = schemas.StrSchema
                    hostName = schemas.StrSchema
                    complianceCheckFastInterval = schemas.Int64Schema
                    complianceCheckInitialDelay = schemas.Int64Schema
                    __annotations__ = {
                        "allowedStatuses": allowedStatuses,
                        "userName": userName,
                        "password": password,
                        "hostName": hostName,
                        "complianceCheckFastInterval": complianceCheckFastInterval,
                        "complianceCheckInitialDelay": complianceCheckInitialDelay,
                    }
            
            password: MetaOapg.properties.password
            userName: MetaOapg.properties.userName
            
            @typing.overload
            def __getitem__(self, name: typing_extensions.Literal["allowedStatuses"]) -> MetaOapg.properties.allowedStatuses: ...
            
            @typing.overload
            def __getitem__(self, name: typing_extensions.Literal["userName"]) -> MetaOapg.properties.userName: ...
            
            @typing.overload
            def __getitem__(self, name: typing_extensions.Literal["password"]) -> MetaOapg.properties.password: ...
            
            @typing.overload
            def __getitem__(self, name: typing_extensions.Literal["hostName"]) -> MetaOapg.properties.hostName: ...
            
            @typing.overload
            def __getitem__(self, name: typing_extensions.Literal["complianceCheckFastInterval"]) -> MetaOapg.properties.complianceCheckFastInterval: ...
            
            @typing.overload
            def __getitem__(self, name: typing_extensions.Literal["complianceCheckInitialDelay"]) -> MetaOapg.properties.complianceCheckInitialDelay: ...
            
            @typing.overload
            def __getitem__(self, name: str) -> schemas.UnsetAnyTypeSchema: ...
            
            def __getitem__(self, name: typing.Union[typing_extensions.Literal["allowedStatuses", "userName", "password", "hostName", "complianceCheckFastInterval", "complianceCheckInitialDelay", ], str]):
                # dict_instance[name] accessor
                return super().__getitem__(name)
            
            
            @typing.overload
            def get_item_oapg(self, name: typing_extensions.Literal["allowedStatuses"]) -> typing.Union[MetaOapg.properties.allowedStatuses, schemas.Unset]: ...
            
            @typing.overload
            def get_item_oapg(self, name: typing_extensions.Literal["userName"]) -> MetaOapg.properties.userName: ...
            
            @typing.overload
            def get_item_oapg(self, name: typing_extensions.Literal["password"]) -> MetaOapg.properties.password: ...
            
            @typing.overload
            def get_item_oapg(self, name: typing_extensions.Literal["hostName"]) -> typing.Union[MetaOapg.properties.hostName, schemas.Unset]: ...
            
            @typing.overload
            def get_item_oapg(self, name: typing_extensions.Literal["complianceCheckFastInterval"]) -> typing.Union[MetaOapg.properties.complianceCheckFastInterval, schemas.Unset]: ...
            
            @typing.overload
            def get_item_oapg(self, name: typing_extensions.Literal["complianceCheckInitialDelay"]) -> typing.Union[MetaOapg.properties.complianceCheckInitialDelay, schemas.Unset]: ...
            
            @typing.overload
            def get_item_oapg(self, name: str) -> typing.Union[schemas.UnsetAnyTypeSchema, schemas.Unset]: ...
            
            def get_item_oapg(self, name: typing.Union[typing_extensions.Literal["allowedStatuses", "userName", "password", "hostName", "complianceCheckFastInterval", "complianceCheckInitialDelay", ], str]):
                return super().get_item_oapg(name)
            
        
            def __new__(
                cls,
                *_args: typing.Union[dict, frozendict.frozendict, ],
                password: typing.Union[MetaOapg.properties.password, str, ],
                userName: typing.Union[MetaOapg.properties.userName, str, ],
                allowedStatuses: typing.Union[MetaOapg.properties.allowedStatuses, list, tuple, schemas.Unset] = schemas.unset,
                hostName: typing.Union[MetaOapg.properties.hostName, str, schemas.Unset] = schemas.unset,
                complianceCheckFastInterval: typing.Union[MetaOapg.properties.complianceCheckFastInterval, decimal.Decimal, int, schemas.Unset] = schemas.unset,
                complianceCheckInitialDelay: typing.Union[MetaOapg.properties.complianceCheckInitialDelay, decimal.Decimal, int, schemas.Unset] = schemas.unset,
                _configuration: typing.Optional[schemas.Configuration] = None,
                **kwargs: typing.Union[schemas.AnyTypeSchema, dict, frozendict.frozendict, str, date, datetime, uuid.UUID, int, float, decimal.Decimal, None, list, tuple, bytes],
            ) -> 'all_of_1':
                return super().__new__(
                    cls,
                    *_args,
                    password=password,
                    userName=userName,
                    allowedStatuses=allowedStatuses,
                    hostName=hostName,
                    complianceCheckFastInterval=complianceCheckFastInterval,
                    complianceCheckInitialDelay=complianceCheckInitialDelay,
                    _configuration=_configuration,
                    **kwargs,
                )
        
        @classmethod
        @functools.lru_cache()
        def all_of(cls):
            # we need this here to make our import statements work
            # we must store _composed_schemas in here so the code is only run
            # when we invoke this method. If we kept this at the class
            # level we would get an error because the class level
            # code would be run when this module is imported, and these composed
            # classes don't exist yet because their module has not finished
            # loading
            return [
                DevicePolicySettings,
                cls.all_of_1,
            ]


    def __new__(
        cls,
        *_args: typing.Union[dict, frozendict.frozendict, str, date, datetime, uuid.UUID, int, float, decimal.Decimal, bool, None, list, tuple, bytes, io.FileIO, io.BufferedReader, ],
        _configuration: typing.Optional[schemas.Configuration] = None,
        **kwargs: typing.Union[schemas.AnyTypeSchema, dict, frozendict.frozendict, str, date, datetime, uuid.UUID, int, float, decimal.Decimal, None, list, tuple, bytes],
    ) -> 'OpswatDevicePolicySettings':
        return super().__new__(
            cls,
            *_args,
            _configuration=_configuration,
            **kwargs,
        )

from openapi_client.model.device_policy_settings import DevicePolicySettings