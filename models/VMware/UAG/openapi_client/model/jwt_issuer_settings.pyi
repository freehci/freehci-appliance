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


class JWTIssuerSettings(
    schemas.DictSchema
):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """


    class MetaOapg:
        
        class properties:
            
            
            class name(
                schemas.StrSchema
            ):
                pass
            issuer = schemas.StrSchema
            
            
            class jwtType(
                schemas.EnumBase,
                schemas.StrSchema
            ):
                
                @schemas.classproperty
                def CONSUMER(cls):
                    return cls("CONSUMER")
                
                @schemas.classproperty
                def PRODUCER(cls):
                    return cls("PRODUCER")
            jsonWebKeySet = schemas.StrSchema
        
            @staticmethod
            def jwtSigningPemCertSettings() -> typing.Type['CertificateChainAndKeyWrapper']:
                return CertificateChainAndKeyWrapper
        
            @staticmethod
            def jwtSigningPfxCertSettings() -> typing.Type['PfxCertStoreWrapper']:
                return PfxCertStoreWrapper
            
            
            class encryptionPublicKey(
                schemas.ListSchema
            ):
            
            
                class MetaOapg:
                    
                    @staticmethod
                    def items() -> typing.Type['PublicKeyOrCert']:
                        return PublicKeyOrCert
            
                def __new__(
                    cls,
                    _arg: typing.Union[typing.Tuple['PublicKeyOrCert'], typing.List['PublicKeyOrCert']],
                    _configuration: typing.Optional[schemas.Configuration] = None,
                ) -> 'encryptionPublicKey':
                    return super().__new__(
                        cls,
                        _arg,
                        _configuration=_configuration,
                    )
            
                def __getitem__(self, i: int) -> 'PublicKeyOrCert':
                    return super().__getitem__(i)
        
            @staticmethod
            def encryptionPublicKeyURLSettings() -> typing.Type['ServerSettings']:
                return ServerSettings
            __annotations__ = {
                "name": name,
                "issuer": issuer,
                "jwtType": jwtType,
                "jsonWebKeySet": jsonWebKeySet,
                "jwtSigningPemCertSettings": jwtSigningPemCertSettings,
                "jwtSigningPfxCertSettings": jwtSigningPfxCertSettings,
                "encryptionPublicKey": encryptionPublicKey,
                "encryptionPublicKeyURLSettings": encryptionPublicKeyURLSettings,
            }
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["name"]) -> MetaOapg.properties.name: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["issuer"]) -> MetaOapg.properties.issuer: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["jwtType"]) -> MetaOapg.properties.jwtType: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["jsonWebKeySet"]) -> MetaOapg.properties.jsonWebKeySet: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["jwtSigningPemCertSettings"]) -> 'CertificateChainAndKeyWrapper': ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["jwtSigningPfxCertSettings"]) -> 'PfxCertStoreWrapper': ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["encryptionPublicKey"]) -> MetaOapg.properties.encryptionPublicKey: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["encryptionPublicKeyURLSettings"]) -> 'ServerSettings': ...
    
    @typing.overload
    def __getitem__(self, name: str) -> schemas.UnsetAnyTypeSchema: ...
    
    def __getitem__(self, name: typing.Union[typing_extensions.Literal["name", "issuer", "jwtType", "jsonWebKeySet", "jwtSigningPemCertSettings", "jwtSigningPfxCertSettings", "encryptionPublicKey", "encryptionPublicKeyURLSettings", ], str]):
        # dict_instance[name] accessor
        return super().__getitem__(name)
    
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["name"]) -> typing.Union[MetaOapg.properties.name, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["issuer"]) -> typing.Union[MetaOapg.properties.issuer, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["jwtType"]) -> typing.Union[MetaOapg.properties.jwtType, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["jsonWebKeySet"]) -> typing.Union[MetaOapg.properties.jsonWebKeySet, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["jwtSigningPemCertSettings"]) -> typing.Union['CertificateChainAndKeyWrapper', schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["jwtSigningPfxCertSettings"]) -> typing.Union['PfxCertStoreWrapper', schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["encryptionPublicKey"]) -> typing.Union[MetaOapg.properties.encryptionPublicKey, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["encryptionPublicKeyURLSettings"]) -> typing.Union['ServerSettings', schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: str) -> typing.Union[schemas.UnsetAnyTypeSchema, schemas.Unset]: ...
    
    def get_item_oapg(self, name: typing.Union[typing_extensions.Literal["name", "issuer", "jwtType", "jsonWebKeySet", "jwtSigningPemCertSettings", "jwtSigningPfxCertSettings", "encryptionPublicKey", "encryptionPublicKeyURLSettings", ], str]):
        return super().get_item_oapg(name)
    

    def __new__(
        cls,
        *_args: typing.Union[dict, frozendict.frozendict, ],
        name: typing.Union[MetaOapg.properties.name, str, schemas.Unset] = schemas.unset,
        issuer: typing.Union[MetaOapg.properties.issuer, str, schemas.Unset] = schemas.unset,
        jwtType: typing.Union[MetaOapg.properties.jwtType, str, schemas.Unset] = schemas.unset,
        jsonWebKeySet: typing.Union[MetaOapg.properties.jsonWebKeySet, str, schemas.Unset] = schemas.unset,
        jwtSigningPemCertSettings: typing.Union['CertificateChainAndKeyWrapper', schemas.Unset] = schemas.unset,
        jwtSigningPfxCertSettings: typing.Union['PfxCertStoreWrapper', schemas.Unset] = schemas.unset,
        encryptionPublicKey: typing.Union[MetaOapg.properties.encryptionPublicKey, list, tuple, schemas.Unset] = schemas.unset,
        encryptionPublicKeyURLSettings: typing.Union['ServerSettings', schemas.Unset] = schemas.unset,
        _configuration: typing.Optional[schemas.Configuration] = None,
        **kwargs: typing.Union[schemas.AnyTypeSchema, dict, frozendict.frozendict, str, date, datetime, uuid.UUID, int, float, decimal.Decimal, None, list, tuple, bytes],
    ) -> 'JWTIssuerSettings':
        return super().__new__(
            cls,
            *_args,
            name=name,
            issuer=issuer,
            jwtType=jwtType,
            jsonWebKeySet=jsonWebKeySet,
            jwtSigningPemCertSettings=jwtSigningPemCertSettings,
            jwtSigningPfxCertSettings=jwtSigningPfxCertSettings,
            encryptionPublicKey=encryptionPublicKey,
            encryptionPublicKeyURLSettings=encryptionPublicKeyURLSettings,
            _configuration=_configuration,
            **kwargs,
        )

from openapi_client.model.certificate_chain_and_key_wrapper import CertificateChainAndKeyWrapper
from openapi_client.model.pfx_cert_store_wrapper import PfxCertStoreWrapper
from openapi_client.model.public_key_or_cert import PublicKeyOrCert
from openapi_client.model.server_settings import ServerSettings
