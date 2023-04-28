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


class AuthMethodSettingsList(
    schemas.DictSchema
):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """


    class MetaOapg:
        
        class properties:
            
            
            class authMethodSettingsList(
                schemas.ListSchema
            ):
            
            
                class MetaOapg:
                    
                    @staticmethod
                    def items() -> typing.Type['AuthMethodSettings']:
                        return AuthMethodSettings
            
                def __new__(
                    cls,
                    _arg: typing.Union[typing.Tuple['AuthMethodSettings'], typing.List['AuthMethodSettings']],
                    _configuration: typing.Optional[schemas.Configuration] = None,
                ) -> 'authMethodSettingsList':
                    return super().__new__(
                        cls,
                        _arg,
                        _configuration=_configuration,
                    )
            
                def __getitem__(self, i: int) -> 'AuthMethodSettings':
                    return super().__getitem__(i)
            __annotations__ = {
                "authMethodSettingsList": authMethodSettingsList,
            }
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["authMethodSettingsList"]) -> MetaOapg.properties.authMethodSettingsList: ...
    
    @typing.overload
    def __getitem__(self, name: str) -> schemas.UnsetAnyTypeSchema: ...
    
    def __getitem__(self, name: typing.Union[typing_extensions.Literal["authMethodSettingsList", ], str]):
        # dict_instance[name] accessor
        return super().__getitem__(name)
    
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["authMethodSettingsList"]) -> typing.Union[MetaOapg.properties.authMethodSettingsList, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: str) -> typing.Union[schemas.UnsetAnyTypeSchema, schemas.Unset]: ...
    
    def get_item_oapg(self, name: typing.Union[typing_extensions.Literal["authMethodSettingsList", ], str]):
        return super().get_item_oapg(name)
    

    def __new__(
        cls,
        *_args: typing.Union[dict, frozendict.frozendict, ],
        authMethodSettingsList: typing.Union[MetaOapg.properties.authMethodSettingsList, list, tuple, schemas.Unset] = schemas.unset,
        _configuration: typing.Optional[schemas.Configuration] = None,
        **kwargs: typing.Union[schemas.AnyTypeSchema, dict, frozendict.frozendict, str, date, datetime, uuid.UUID, int, float, decimal.Decimal, None, list, tuple, bytes],
    ) -> 'AuthMethodSettingsList':
        return super().__new__(
            cls,
            *_args,
            authMethodSettingsList=authMethodSettingsList,
            _configuration=_configuration,
            **kwargs,
        )

from openapi_client.model.auth_method_settings import AuthMethodSettings
