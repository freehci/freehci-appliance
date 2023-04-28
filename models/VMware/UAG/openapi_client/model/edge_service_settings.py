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


class EdgeServiceSettings(
    schemas.DictSchema
):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """


    class MetaOapg:
        required = {
            "identifier",
            "enabled",
        }
        
        @staticmethod
        def discriminator():
            return {
                'identifier': {
                    'AirWatchCGEdgeServiceSettings': AirWatchCGEdgeServiceSettings,
                    'AirWatchSEGEdgeServiceSettings': AirWatchSEGEdgeServiceSettings,
                    'AirWatchTunnelProxyEdgeServiceSettings': AirWatchTunnelProxyEdgeServiceSettings,
                    'AirWatchTunnelServerEdgeServiceSettings': AirWatchTunnelServerEdgeServiceSettings,
                    'ViewEdgeServiceSettings': ViewEdgeServiceSettings,
                    'WsPortalEdgeServiceSettings': WsPortalEdgeServiceSettings,
                }
            }
        
        class properties:
            enabled = schemas.BoolSchema
            identifier = schemas.StrSchema
            proxyDestinationUrl = schemas.StrSchema
            
            
            class proxyDestinationUrlThumbprints(
                schemas.StrSchema
            ):
            
            
                class MetaOapg:
                    regex=[{
                        'pattern': r'^\s*$||(((sha1|md5|sha256|sha384|sha512)=)?([0-9a-fA-F][0-9a-fA-F][: ]?)*[0-9a-fA-F][0-9a-fA-F], *)*(((sha1|md5|sha256|sha384|sha512)=)?([0-9a-fA-F][0-9a-fA-F][: ]?)*[0-9a-fA-F][0-9a-fA-F])',  # noqa: E501
                    }]
            authMethods = schemas.StrSchema
            healthCheckUrl = schemas.StrSchema
            samlSP = schemas.StrSchema
            
            
            class hostEntries(
                schemas.ListSchema
            ):
            
            
                class MetaOapg:
                    items = schemas.StrSchema
            
                def __new__(
                    cls,
                    _arg: typing.Union[typing.Tuple[typing.Union[MetaOapg.items, str, ]], typing.List[typing.Union[MetaOapg.items, str, ]]],
                    _configuration: typing.Optional[schemas.Configuration] = None,
                ) -> 'hostEntries':
                    return super().__new__(
                        cls,
                        _arg,
                        _configuration=_configuration,
                    )
            
                def __getitem__(self, i: int) -> MetaOapg.items:
                    return super().__getitem__(i)
            
            
            class trustedCertificates(
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
                ) -> 'trustedCertificates':
                    return super().__new__(
                        cls,
                        _arg,
                        _configuration=_configuration,
                    )
            
                def __getitem__(self, i: int) -> 'PublicKeyOrCert':
                    return super().__getitem__(i)
            
            
            class devicePolicyServiceProvider(
                schemas.EnumBase,
                schemas.StrSchema
            ):
            
            
                class MetaOapg:
                    enum_value_to_name = {
                        "OPSWAT": "OPSWAT",
                        "Workspace_ONE_Intelligence_Risk_Score": "WORKSPACE_ONE_INTELLIGENCE_RISK_SCORE",
                    }
                
                @schemas.classproperty
                def OPSWAT(cls):
                    return cls("OPSWAT")
                
                @schemas.classproperty
                def WORKSPACE_ONE_INTELLIGENCE_RISK_SCORE(cls):
                    return cls("Workspace_ONE_Intelligence_Risk_Score")
            
            
            class customExecutableList(
                schemas.ListSchema
            ):
            
            
                class MetaOapg:
                    items = schemas.StrSchema
            
                def __new__(
                    cls,
                    _arg: typing.Union[typing.Tuple[typing.Union[MetaOapg.items, str, ]], typing.List[typing.Union[MetaOapg.items, str, ]]],
                    _configuration: typing.Optional[schemas.Configuration] = None,
                ) -> 'customExecutableList':
                    return super().__new__(
                        cls,
                        _arg,
                        _configuration=_configuration,
                    )
            
                def __getitem__(self, i: int) -> MetaOapg.items:
                    return super().__getitem__(i)
            redirectHostPortMappingList = schemas.StrSchema
            canonicalizationEnabled = schemas.BoolSchema
            hostRedirectionEnabled = schemas.BoolSchema
            uniqueInstanceId = schemas.StrSchema
            __annotations__ = {
                "enabled": enabled,
                "identifier": identifier,
                "proxyDestinationUrl": proxyDestinationUrl,
                "proxyDestinationUrlThumbprints": proxyDestinationUrlThumbprints,
                "authMethods": authMethods,
                "healthCheckUrl": healthCheckUrl,
                "samlSP": samlSP,
                "hostEntries": hostEntries,
                "trustedCertificates": trustedCertificates,
                "devicePolicyServiceProvider": devicePolicyServiceProvider,
                "customExecutableList": customExecutableList,
                "redirectHostPortMappingList": redirectHostPortMappingList,
                "canonicalizationEnabled": canonicalizationEnabled,
                "hostRedirectionEnabled": hostRedirectionEnabled,
                "uniqueInstanceId": uniqueInstanceId,
            }
    
    identifier: MetaOapg.properties.identifier
    enabled: MetaOapg.properties.enabled
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["enabled"]) -> MetaOapg.properties.enabled: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["identifier"]) -> MetaOapg.properties.identifier: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["proxyDestinationUrl"]) -> MetaOapg.properties.proxyDestinationUrl: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["proxyDestinationUrlThumbprints"]) -> MetaOapg.properties.proxyDestinationUrlThumbprints: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["authMethods"]) -> MetaOapg.properties.authMethods: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["healthCheckUrl"]) -> MetaOapg.properties.healthCheckUrl: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["samlSP"]) -> MetaOapg.properties.samlSP: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["hostEntries"]) -> MetaOapg.properties.hostEntries: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["trustedCertificates"]) -> MetaOapg.properties.trustedCertificates: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["devicePolicyServiceProvider"]) -> MetaOapg.properties.devicePolicyServiceProvider: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["customExecutableList"]) -> MetaOapg.properties.customExecutableList: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["redirectHostPortMappingList"]) -> MetaOapg.properties.redirectHostPortMappingList: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["canonicalizationEnabled"]) -> MetaOapg.properties.canonicalizationEnabled: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["hostRedirectionEnabled"]) -> MetaOapg.properties.hostRedirectionEnabled: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["uniqueInstanceId"]) -> MetaOapg.properties.uniqueInstanceId: ...
    
    @typing.overload
    def __getitem__(self, name: str) -> schemas.UnsetAnyTypeSchema: ...
    
    def __getitem__(self, name: typing.Union[typing_extensions.Literal["enabled", "identifier", "proxyDestinationUrl", "proxyDestinationUrlThumbprints", "authMethods", "healthCheckUrl", "samlSP", "hostEntries", "trustedCertificates", "devicePolicyServiceProvider", "customExecutableList", "redirectHostPortMappingList", "canonicalizationEnabled", "hostRedirectionEnabled", "uniqueInstanceId", ], str]):
        # dict_instance[name] accessor
        return super().__getitem__(name)
    
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["enabled"]) -> MetaOapg.properties.enabled: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["identifier"]) -> MetaOapg.properties.identifier: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["proxyDestinationUrl"]) -> typing.Union[MetaOapg.properties.proxyDestinationUrl, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["proxyDestinationUrlThumbprints"]) -> typing.Union[MetaOapg.properties.proxyDestinationUrlThumbprints, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["authMethods"]) -> typing.Union[MetaOapg.properties.authMethods, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["healthCheckUrl"]) -> typing.Union[MetaOapg.properties.healthCheckUrl, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["samlSP"]) -> typing.Union[MetaOapg.properties.samlSP, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["hostEntries"]) -> typing.Union[MetaOapg.properties.hostEntries, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["trustedCertificates"]) -> typing.Union[MetaOapg.properties.trustedCertificates, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["devicePolicyServiceProvider"]) -> typing.Union[MetaOapg.properties.devicePolicyServiceProvider, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["customExecutableList"]) -> typing.Union[MetaOapg.properties.customExecutableList, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["redirectHostPortMappingList"]) -> typing.Union[MetaOapg.properties.redirectHostPortMappingList, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["canonicalizationEnabled"]) -> typing.Union[MetaOapg.properties.canonicalizationEnabled, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["hostRedirectionEnabled"]) -> typing.Union[MetaOapg.properties.hostRedirectionEnabled, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["uniqueInstanceId"]) -> typing.Union[MetaOapg.properties.uniqueInstanceId, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: str) -> typing.Union[schemas.UnsetAnyTypeSchema, schemas.Unset]: ...
    
    def get_item_oapg(self, name: typing.Union[typing_extensions.Literal["enabled", "identifier", "proxyDestinationUrl", "proxyDestinationUrlThumbprints", "authMethods", "healthCheckUrl", "samlSP", "hostEntries", "trustedCertificates", "devicePolicyServiceProvider", "customExecutableList", "redirectHostPortMappingList", "canonicalizationEnabled", "hostRedirectionEnabled", "uniqueInstanceId", ], str]):
        return super().get_item_oapg(name)
    

    def __new__(
        cls,
        *_args: typing.Union[dict, frozendict.frozendict, ],
        identifier: typing.Union[MetaOapg.properties.identifier, str, ],
        enabled: typing.Union[MetaOapg.properties.enabled, bool, ],
        proxyDestinationUrl: typing.Union[MetaOapg.properties.proxyDestinationUrl, str, schemas.Unset] = schemas.unset,
        proxyDestinationUrlThumbprints: typing.Union[MetaOapg.properties.proxyDestinationUrlThumbprints, str, schemas.Unset] = schemas.unset,
        authMethods: typing.Union[MetaOapg.properties.authMethods, str, schemas.Unset] = schemas.unset,
        healthCheckUrl: typing.Union[MetaOapg.properties.healthCheckUrl, str, schemas.Unset] = schemas.unset,
        samlSP: typing.Union[MetaOapg.properties.samlSP, str, schemas.Unset] = schemas.unset,
        hostEntries: typing.Union[MetaOapg.properties.hostEntries, list, tuple, schemas.Unset] = schemas.unset,
        trustedCertificates: typing.Union[MetaOapg.properties.trustedCertificates, list, tuple, schemas.Unset] = schemas.unset,
        devicePolicyServiceProvider: typing.Union[MetaOapg.properties.devicePolicyServiceProvider, str, schemas.Unset] = schemas.unset,
        customExecutableList: typing.Union[MetaOapg.properties.customExecutableList, list, tuple, schemas.Unset] = schemas.unset,
        redirectHostPortMappingList: typing.Union[MetaOapg.properties.redirectHostPortMappingList, str, schemas.Unset] = schemas.unset,
        canonicalizationEnabled: typing.Union[MetaOapg.properties.canonicalizationEnabled, bool, schemas.Unset] = schemas.unset,
        hostRedirectionEnabled: typing.Union[MetaOapg.properties.hostRedirectionEnabled, bool, schemas.Unset] = schemas.unset,
        uniqueInstanceId: typing.Union[MetaOapg.properties.uniqueInstanceId, str, schemas.Unset] = schemas.unset,
        _configuration: typing.Optional[schemas.Configuration] = None,
        **kwargs: typing.Union[schemas.AnyTypeSchema, dict, frozendict.frozendict, str, date, datetime, uuid.UUID, int, float, decimal.Decimal, None, list, tuple, bytes],
    ) -> 'EdgeServiceSettings':
        return super().__new__(
            cls,
            *_args,
            identifier=identifier,
            enabled=enabled,
            proxyDestinationUrl=proxyDestinationUrl,
            proxyDestinationUrlThumbprints=proxyDestinationUrlThumbprints,
            authMethods=authMethods,
            healthCheckUrl=healthCheckUrl,
            samlSP=samlSP,
            hostEntries=hostEntries,
            trustedCertificates=trustedCertificates,
            devicePolicyServiceProvider=devicePolicyServiceProvider,
            customExecutableList=customExecutableList,
            redirectHostPortMappingList=redirectHostPortMappingList,
            canonicalizationEnabled=canonicalizationEnabled,
            hostRedirectionEnabled=hostRedirectionEnabled,
            uniqueInstanceId=uniqueInstanceId,
            _configuration=_configuration,
            **kwargs,
        )

from openapi_client.model.air_watch_cg_edge_service_settings import AirWatchCGEdgeServiceSettings
from openapi_client.model.air_watch_seg_edge_service_settings import AirWatchSEGEdgeServiceSettings
from openapi_client.model.air_watch_tunnel_proxy_edge_service_settings import AirWatchTunnelProxyEdgeServiceSettings
from openapi_client.model.air_watch_tunnel_server_edge_service_settings import AirWatchTunnelServerEdgeServiceSettings
from openapi_client.model.public_key_or_cert import PublicKeyOrCert
from openapi_client.model.view_edge_service_settings import ViewEdgeServiceSettings
from openapi_client.model.ws_portal_edge_service_settings import WsPortalEdgeServiceSettings
