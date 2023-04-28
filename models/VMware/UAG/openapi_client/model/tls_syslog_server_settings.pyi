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


class TlsSyslogServerSettings(
    schemas.DictSchema
):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """


    class MetaOapg:
        
        class properties:
            hostname = schemas.StrSchema
            port = schemas.Int32Schema
            acceptedPeer = schemas.StrSchema
            syslogServerCACertPemV2 = schemas.StrSchema
            syslogClientCertPemV2 = schemas.StrSchema
            syslogClientCertKeyPemV2 = schemas.StrSchema
            __annotations__ = {
                "hostname": hostname,
                "port": port,
                "acceptedPeer": acceptedPeer,
                "syslogServerCACertPemV2": syslogServerCACertPemV2,
                "syslogClientCertPemV2": syslogClientCertPemV2,
                "syslogClientCertKeyPemV2": syslogClientCertKeyPemV2,
            }
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["hostname"]) -> MetaOapg.properties.hostname: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["port"]) -> MetaOapg.properties.port: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["acceptedPeer"]) -> MetaOapg.properties.acceptedPeer: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["syslogServerCACertPemV2"]) -> MetaOapg.properties.syslogServerCACertPemV2: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["syslogClientCertPemV2"]) -> MetaOapg.properties.syslogClientCertPemV2: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["syslogClientCertKeyPemV2"]) -> MetaOapg.properties.syslogClientCertKeyPemV2: ...
    
    @typing.overload
    def __getitem__(self, name: str) -> schemas.UnsetAnyTypeSchema: ...
    
    def __getitem__(self, name: typing.Union[typing_extensions.Literal["hostname", "port", "acceptedPeer", "syslogServerCACertPemV2", "syslogClientCertPemV2", "syslogClientCertKeyPemV2", ], str]):
        # dict_instance[name] accessor
        return super().__getitem__(name)
    
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["hostname"]) -> typing.Union[MetaOapg.properties.hostname, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["port"]) -> typing.Union[MetaOapg.properties.port, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["acceptedPeer"]) -> typing.Union[MetaOapg.properties.acceptedPeer, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["syslogServerCACertPemV2"]) -> typing.Union[MetaOapg.properties.syslogServerCACertPemV2, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["syslogClientCertPemV2"]) -> typing.Union[MetaOapg.properties.syslogClientCertPemV2, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["syslogClientCertKeyPemV2"]) -> typing.Union[MetaOapg.properties.syslogClientCertKeyPemV2, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: str) -> typing.Union[schemas.UnsetAnyTypeSchema, schemas.Unset]: ...
    
    def get_item_oapg(self, name: typing.Union[typing_extensions.Literal["hostname", "port", "acceptedPeer", "syslogServerCACertPemV2", "syslogClientCertPemV2", "syslogClientCertKeyPemV2", ], str]):
        return super().get_item_oapg(name)
    

    def __new__(
        cls,
        *_args: typing.Union[dict, frozendict.frozendict, ],
        hostname: typing.Union[MetaOapg.properties.hostname, str, schemas.Unset] = schemas.unset,
        port: typing.Union[MetaOapg.properties.port, decimal.Decimal, int, schemas.Unset] = schemas.unset,
        acceptedPeer: typing.Union[MetaOapg.properties.acceptedPeer, str, schemas.Unset] = schemas.unset,
        syslogServerCACertPemV2: typing.Union[MetaOapg.properties.syslogServerCACertPemV2, str, schemas.Unset] = schemas.unset,
        syslogClientCertPemV2: typing.Union[MetaOapg.properties.syslogClientCertPemV2, str, schemas.Unset] = schemas.unset,
        syslogClientCertKeyPemV2: typing.Union[MetaOapg.properties.syslogClientCertKeyPemV2, str, schemas.Unset] = schemas.unset,
        _configuration: typing.Optional[schemas.Configuration] = None,
        **kwargs: typing.Union[schemas.AnyTypeSchema, dict, frozendict.frozendict, str, date, datetime, uuid.UUID, int, float, decimal.Decimal, None, list, tuple, bytes],
    ) -> 'TlsSyslogServerSettings':
        return super().__new__(
            cls,
            *_args,
            hostname=hostname,
            port=port,
            acceptedPeer=acceptedPeer,
            syslogServerCACertPemV2=syslogServerCACertPemV2,
            syslogClientCertPemV2=syslogClientCertPemV2,
            syslogClientCertKeyPemV2=syslogClientCertKeyPemV2,
            _configuration=_configuration,
            **kwargs,
        )