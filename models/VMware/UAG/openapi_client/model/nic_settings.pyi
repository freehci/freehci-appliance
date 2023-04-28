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


class NicSettings(
    schemas.DictSchema
):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """


    class MetaOapg:
        required = {
            "allocationMode",
            "ipv4Address",
            "ipv4Netmask",
            "nic",
        }
        
        class properties:
            ipv4Address = schemas.StrSchema
            ipv4Netmask = schemas.StrSchema
            
            
            class nic(
                schemas.EnumBase,
                schemas.StrSchema
            ):
                
                @schemas.classproperty
                def ETH0(cls):
                    return cls("eth0")
                
                @schemas.classproperty
                def ETH1(cls):
                    return cls("eth1")
                
                @schemas.classproperty
                def ETH2(cls):
                    return cls("eth2")
            
            
            class allocationMode(
                schemas.EnumBase,
                schemas.StrSchema
            ):
                
                @schemas.classproperty
                def STATICV4(cls):
                    return cls("STATICV4")
                
                @schemas.classproperty
                def STATICV6(cls):
                    return cls("STATICV6")
                
                @schemas.classproperty
                def DHCPV4(cls):
                    return cls("DHCPV4")
                
                @schemas.classproperty
                def DHCPV6(cls):
                    return cls("DHCPV6")
                
                @schemas.classproperty
                def AUTOV6(cls):
                    return cls("AUTOV6")
                
                @schemas.classproperty
                def STATICV4_STATICV6(cls):
                    return cls("STATICV4_STATICV6")
                
                @schemas.classproperty
                def STATICV4_DHCPV6(cls):
                    return cls("STATICV4_DHCPV6")
                
                @schemas.classproperty
                def STATICV4_AUTOV6(cls):
                    return cls("STATICV4_AUTOV6")
                
                @schemas.classproperty
                def DHCPV4_STATICV6(cls):
                    return cls("DHCPV4_STATICV6")
                
                @schemas.classproperty
                def DHCPV4_DHCPV6(cls):
                    return cls("DHCPV4_DHCPV6")
                
                @schemas.classproperty
                def DHCPV4_AUTOV6(cls):
                    return cls("DHCPV4_AUTOV6")
                
                @schemas.classproperty
                def STATIC(cls):
                    return cls("Static")
                
                @schemas.classproperty
                def DYNAMIC(cls):
                    return cls("Dynamic")
            ipv4DefaultGateway = schemas.StrSchema
            ipv4StaticRoutes = schemas.StrSchema
            
            
            class customConfig(
                schemas.StrSchema
            ):
                pass
            __annotations__ = {
                "ipv4Address": ipv4Address,
                "ipv4Netmask": ipv4Netmask,
                "nic": nic,
                "allocationMode": allocationMode,
                "ipv4DefaultGateway": ipv4DefaultGateway,
                "ipv4StaticRoutes": ipv4StaticRoutes,
                "customConfig": customConfig,
            }
    
    allocationMode: MetaOapg.properties.allocationMode
    ipv4Address: MetaOapg.properties.ipv4Address
    ipv4Netmask: MetaOapg.properties.ipv4Netmask
    nic: MetaOapg.properties.nic
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["ipv4Address"]) -> MetaOapg.properties.ipv4Address: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["ipv4Netmask"]) -> MetaOapg.properties.ipv4Netmask: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["nic"]) -> MetaOapg.properties.nic: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["allocationMode"]) -> MetaOapg.properties.allocationMode: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["ipv4DefaultGateway"]) -> MetaOapg.properties.ipv4DefaultGateway: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["ipv4StaticRoutes"]) -> MetaOapg.properties.ipv4StaticRoutes: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["customConfig"]) -> MetaOapg.properties.customConfig: ...
    
    @typing.overload
    def __getitem__(self, name: str) -> schemas.UnsetAnyTypeSchema: ...
    
    def __getitem__(self, name: typing.Union[typing_extensions.Literal["ipv4Address", "ipv4Netmask", "nic", "allocationMode", "ipv4DefaultGateway", "ipv4StaticRoutes", "customConfig", ], str]):
        # dict_instance[name] accessor
        return super().__getitem__(name)
    
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["ipv4Address"]) -> MetaOapg.properties.ipv4Address: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["ipv4Netmask"]) -> MetaOapg.properties.ipv4Netmask: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["nic"]) -> MetaOapg.properties.nic: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["allocationMode"]) -> MetaOapg.properties.allocationMode: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["ipv4DefaultGateway"]) -> typing.Union[MetaOapg.properties.ipv4DefaultGateway, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["ipv4StaticRoutes"]) -> typing.Union[MetaOapg.properties.ipv4StaticRoutes, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["customConfig"]) -> typing.Union[MetaOapg.properties.customConfig, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: str) -> typing.Union[schemas.UnsetAnyTypeSchema, schemas.Unset]: ...
    
    def get_item_oapg(self, name: typing.Union[typing_extensions.Literal["ipv4Address", "ipv4Netmask", "nic", "allocationMode", "ipv4DefaultGateway", "ipv4StaticRoutes", "customConfig", ], str]):
        return super().get_item_oapg(name)
    

    def __new__(
        cls,
        *_args: typing.Union[dict, frozendict.frozendict, ],
        allocationMode: typing.Union[MetaOapg.properties.allocationMode, str, ],
        ipv4Address: typing.Union[MetaOapg.properties.ipv4Address, str, ],
        ipv4Netmask: typing.Union[MetaOapg.properties.ipv4Netmask, str, ],
        nic: typing.Union[MetaOapg.properties.nic, str, ],
        ipv4DefaultGateway: typing.Union[MetaOapg.properties.ipv4DefaultGateway, str, schemas.Unset] = schemas.unset,
        ipv4StaticRoutes: typing.Union[MetaOapg.properties.ipv4StaticRoutes, str, schemas.Unset] = schemas.unset,
        customConfig: typing.Union[MetaOapg.properties.customConfig, str, schemas.Unset] = schemas.unset,
        _configuration: typing.Optional[schemas.Configuration] = None,
        **kwargs: typing.Union[schemas.AnyTypeSchema, dict, frozendict.frozendict, str, date, datetime, uuid.UUID, int, float, decimal.Decimal, None, list, tuple, bytes],
    ) -> 'NicSettings':
        return super().__new__(
            cls,
            *_args,
            allocationMode=allocationMode,
            ipv4Address=ipv4Address,
            ipv4Netmask=ipv4Netmask,
            nic=nic,
            ipv4DefaultGateway=ipv4DefaultGateway,
            ipv4StaticRoutes=ipv4StaticRoutes,
            customConfig=customConfig,
            _configuration=_configuration,
            **kwargs,
        )
