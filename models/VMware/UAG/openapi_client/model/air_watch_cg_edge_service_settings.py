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


class AirWatchCGEdgeServiceSettings(
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
                    "airwatchComponentsInstalled",
                    "apiServerUsername",
                    "organizationGroupCode",
                    "apiServerUrl",
                    "apiServerPassword",
                    "airwatchServerHostname",
                }
                
                class properties:
                    apiServerUrl = schemas.StrSchema
                    apiServerUsername = schemas.StrSchema
                    apiServerPassword = schemas.StrSchema
                    organizationGroupCode = schemas.StrSchema
                    airwatchServerHostname = schemas.StrSchema
                    reinitializeGatewayProcess = schemas.BoolSchema
                    outboundProxyHost = schemas.StrSchema
                    outboundProxyPort = schemas.StrSchema
                    outboundProxyUsername = schemas.StrSchema
                    ntlmAuthentication = schemas.BoolSchema
                    outboundProxyPassword = schemas.StrSchema
                    airwatchOutboundProxy = schemas.BoolSchema
                    airwatchComponentsInstalled = schemas.StrSchema
                    airwatchAgentStartUpMode = schemas.StrSchema
                    serviceHost = schemas.StrSchema
                    servicePort = schemas.StrSchema
                    serviceStatsPort = schemas.StrSchema
                    serviceName = schemas.StrSchema
                    serviceInstallStatus = schemas.BoolSchema
                    serviceInstallationMessage = schemas.StrSchema
                    runningMode = schemas.StrSchema
                    serviceConfigurationFailed = schemas.BoolSchema
                    cgConfigurationId = schemas.StrSchema
                    __annotations__ = {
                        "apiServerUrl": apiServerUrl,
                        "apiServerUsername": apiServerUsername,
                        "apiServerPassword": apiServerPassword,
                        "organizationGroupCode": organizationGroupCode,
                        "airwatchServerHostname": airwatchServerHostname,
                        "reinitializeGatewayProcess": reinitializeGatewayProcess,
                        "outboundProxyHost": outboundProxyHost,
                        "outboundProxyPort": outboundProxyPort,
                        "outboundProxyUsername": outboundProxyUsername,
                        "ntlmAuthentication": ntlmAuthentication,
                        "outboundProxyPassword": outboundProxyPassword,
                        "airwatchOutboundProxy": airwatchOutboundProxy,
                        "airwatchComponentsInstalled": airwatchComponentsInstalled,
                        "airwatchAgentStartUpMode": airwatchAgentStartUpMode,
                        "serviceHost": serviceHost,
                        "servicePort": servicePort,
                        "serviceStatsPort": serviceStatsPort,
                        "serviceName": serviceName,
                        "serviceInstallStatus": serviceInstallStatus,
                        "serviceInstallationMessage": serviceInstallationMessage,
                        "runningMode": runningMode,
                        "serviceConfigurationFailed": serviceConfigurationFailed,
                        "cgConfigurationId": cgConfigurationId,
                    }
            
            airwatchComponentsInstalled: MetaOapg.properties.airwatchComponentsInstalled
            apiServerUsername: MetaOapg.properties.apiServerUsername
            organizationGroupCode: MetaOapg.properties.organizationGroupCode
            apiServerUrl: MetaOapg.properties.apiServerUrl
            apiServerPassword: MetaOapg.properties.apiServerPassword
            airwatchServerHostname: MetaOapg.properties.airwatchServerHostname
            
            @typing.overload
            def __getitem__(self, name: typing_extensions.Literal["apiServerUrl"]) -> MetaOapg.properties.apiServerUrl: ...
            
            @typing.overload
            def __getitem__(self, name: typing_extensions.Literal["apiServerUsername"]) -> MetaOapg.properties.apiServerUsername: ...
            
            @typing.overload
            def __getitem__(self, name: typing_extensions.Literal["apiServerPassword"]) -> MetaOapg.properties.apiServerPassword: ...
            
            @typing.overload
            def __getitem__(self, name: typing_extensions.Literal["organizationGroupCode"]) -> MetaOapg.properties.organizationGroupCode: ...
            
            @typing.overload
            def __getitem__(self, name: typing_extensions.Literal["airwatchServerHostname"]) -> MetaOapg.properties.airwatchServerHostname: ...
            
            @typing.overload
            def __getitem__(self, name: typing_extensions.Literal["reinitializeGatewayProcess"]) -> MetaOapg.properties.reinitializeGatewayProcess: ...
            
            @typing.overload
            def __getitem__(self, name: typing_extensions.Literal["outboundProxyHost"]) -> MetaOapg.properties.outboundProxyHost: ...
            
            @typing.overload
            def __getitem__(self, name: typing_extensions.Literal["outboundProxyPort"]) -> MetaOapg.properties.outboundProxyPort: ...
            
            @typing.overload
            def __getitem__(self, name: typing_extensions.Literal["outboundProxyUsername"]) -> MetaOapg.properties.outboundProxyUsername: ...
            
            @typing.overload
            def __getitem__(self, name: typing_extensions.Literal["ntlmAuthentication"]) -> MetaOapg.properties.ntlmAuthentication: ...
            
            @typing.overload
            def __getitem__(self, name: typing_extensions.Literal["outboundProxyPassword"]) -> MetaOapg.properties.outboundProxyPassword: ...
            
            @typing.overload
            def __getitem__(self, name: typing_extensions.Literal["airwatchOutboundProxy"]) -> MetaOapg.properties.airwatchOutboundProxy: ...
            
            @typing.overload
            def __getitem__(self, name: typing_extensions.Literal["airwatchComponentsInstalled"]) -> MetaOapg.properties.airwatchComponentsInstalled: ...
            
            @typing.overload
            def __getitem__(self, name: typing_extensions.Literal["airwatchAgentStartUpMode"]) -> MetaOapg.properties.airwatchAgentStartUpMode: ...
            
            @typing.overload
            def __getitem__(self, name: typing_extensions.Literal["serviceHost"]) -> MetaOapg.properties.serviceHost: ...
            
            @typing.overload
            def __getitem__(self, name: typing_extensions.Literal["servicePort"]) -> MetaOapg.properties.servicePort: ...
            
            @typing.overload
            def __getitem__(self, name: typing_extensions.Literal["serviceStatsPort"]) -> MetaOapg.properties.serviceStatsPort: ...
            
            @typing.overload
            def __getitem__(self, name: typing_extensions.Literal["serviceName"]) -> MetaOapg.properties.serviceName: ...
            
            @typing.overload
            def __getitem__(self, name: typing_extensions.Literal["serviceInstallStatus"]) -> MetaOapg.properties.serviceInstallStatus: ...
            
            @typing.overload
            def __getitem__(self, name: typing_extensions.Literal["serviceInstallationMessage"]) -> MetaOapg.properties.serviceInstallationMessage: ...
            
            @typing.overload
            def __getitem__(self, name: typing_extensions.Literal["runningMode"]) -> MetaOapg.properties.runningMode: ...
            
            @typing.overload
            def __getitem__(self, name: typing_extensions.Literal["serviceConfigurationFailed"]) -> MetaOapg.properties.serviceConfigurationFailed: ...
            
            @typing.overload
            def __getitem__(self, name: typing_extensions.Literal["cgConfigurationId"]) -> MetaOapg.properties.cgConfigurationId: ...
            
            @typing.overload
            def __getitem__(self, name: str) -> schemas.UnsetAnyTypeSchema: ...
            
            def __getitem__(self, name: typing.Union[typing_extensions.Literal["apiServerUrl", "apiServerUsername", "apiServerPassword", "organizationGroupCode", "airwatchServerHostname", "reinitializeGatewayProcess", "outboundProxyHost", "outboundProxyPort", "outboundProxyUsername", "ntlmAuthentication", "outboundProxyPassword", "airwatchOutboundProxy", "airwatchComponentsInstalled", "airwatchAgentStartUpMode", "serviceHost", "servicePort", "serviceStatsPort", "serviceName", "serviceInstallStatus", "serviceInstallationMessage", "runningMode", "serviceConfigurationFailed", "cgConfigurationId", ], str]):
                # dict_instance[name] accessor
                return super().__getitem__(name)
            
            
            @typing.overload
            def get_item_oapg(self, name: typing_extensions.Literal["apiServerUrl"]) -> MetaOapg.properties.apiServerUrl: ...
            
            @typing.overload
            def get_item_oapg(self, name: typing_extensions.Literal["apiServerUsername"]) -> MetaOapg.properties.apiServerUsername: ...
            
            @typing.overload
            def get_item_oapg(self, name: typing_extensions.Literal["apiServerPassword"]) -> MetaOapg.properties.apiServerPassword: ...
            
            @typing.overload
            def get_item_oapg(self, name: typing_extensions.Literal["organizationGroupCode"]) -> MetaOapg.properties.organizationGroupCode: ...
            
            @typing.overload
            def get_item_oapg(self, name: typing_extensions.Literal["airwatchServerHostname"]) -> MetaOapg.properties.airwatchServerHostname: ...
            
            @typing.overload
            def get_item_oapg(self, name: typing_extensions.Literal["reinitializeGatewayProcess"]) -> typing.Union[MetaOapg.properties.reinitializeGatewayProcess, schemas.Unset]: ...
            
            @typing.overload
            def get_item_oapg(self, name: typing_extensions.Literal["outboundProxyHost"]) -> typing.Union[MetaOapg.properties.outboundProxyHost, schemas.Unset]: ...
            
            @typing.overload
            def get_item_oapg(self, name: typing_extensions.Literal["outboundProxyPort"]) -> typing.Union[MetaOapg.properties.outboundProxyPort, schemas.Unset]: ...
            
            @typing.overload
            def get_item_oapg(self, name: typing_extensions.Literal["outboundProxyUsername"]) -> typing.Union[MetaOapg.properties.outboundProxyUsername, schemas.Unset]: ...
            
            @typing.overload
            def get_item_oapg(self, name: typing_extensions.Literal["ntlmAuthentication"]) -> typing.Union[MetaOapg.properties.ntlmAuthentication, schemas.Unset]: ...
            
            @typing.overload
            def get_item_oapg(self, name: typing_extensions.Literal["outboundProxyPassword"]) -> typing.Union[MetaOapg.properties.outboundProxyPassword, schemas.Unset]: ...
            
            @typing.overload
            def get_item_oapg(self, name: typing_extensions.Literal["airwatchOutboundProxy"]) -> typing.Union[MetaOapg.properties.airwatchOutboundProxy, schemas.Unset]: ...
            
            @typing.overload
            def get_item_oapg(self, name: typing_extensions.Literal["airwatchComponentsInstalled"]) -> MetaOapg.properties.airwatchComponentsInstalled: ...
            
            @typing.overload
            def get_item_oapg(self, name: typing_extensions.Literal["airwatchAgentStartUpMode"]) -> typing.Union[MetaOapg.properties.airwatchAgentStartUpMode, schemas.Unset]: ...
            
            @typing.overload
            def get_item_oapg(self, name: typing_extensions.Literal["serviceHost"]) -> typing.Union[MetaOapg.properties.serviceHost, schemas.Unset]: ...
            
            @typing.overload
            def get_item_oapg(self, name: typing_extensions.Literal["servicePort"]) -> typing.Union[MetaOapg.properties.servicePort, schemas.Unset]: ...
            
            @typing.overload
            def get_item_oapg(self, name: typing_extensions.Literal["serviceStatsPort"]) -> typing.Union[MetaOapg.properties.serviceStatsPort, schemas.Unset]: ...
            
            @typing.overload
            def get_item_oapg(self, name: typing_extensions.Literal["serviceName"]) -> typing.Union[MetaOapg.properties.serviceName, schemas.Unset]: ...
            
            @typing.overload
            def get_item_oapg(self, name: typing_extensions.Literal["serviceInstallStatus"]) -> typing.Union[MetaOapg.properties.serviceInstallStatus, schemas.Unset]: ...
            
            @typing.overload
            def get_item_oapg(self, name: typing_extensions.Literal["serviceInstallationMessage"]) -> typing.Union[MetaOapg.properties.serviceInstallationMessage, schemas.Unset]: ...
            
            @typing.overload
            def get_item_oapg(self, name: typing_extensions.Literal["runningMode"]) -> typing.Union[MetaOapg.properties.runningMode, schemas.Unset]: ...
            
            @typing.overload
            def get_item_oapg(self, name: typing_extensions.Literal["serviceConfigurationFailed"]) -> typing.Union[MetaOapg.properties.serviceConfigurationFailed, schemas.Unset]: ...
            
            @typing.overload
            def get_item_oapg(self, name: typing_extensions.Literal["cgConfigurationId"]) -> typing.Union[MetaOapg.properties.cgConfigurationId, schemas.Unset]: ...
            
            @typing.overload
            def get_item_oapg(self, name: str) -> typing.Union[schemas.UnsetAnyTypeSchema, schemas.Unset]: ...
            
            def get_item_oapg(self, name: typing.Union[typing_extensions.Literal["apiServerUrl", "apiServerUsername", "apiServerPassword", "organizationGroupCode", "airwatchServerHostname", "reinitializeGatewayProcess", "outboundProxyHost", "outboundProxyPort", "outboundProxyUsername", "ntlmAuthentication", "outboundProxyPassword", "airwatchOutboundProxy", "airwatchComponentsInstalled", "airwatchAgentStartUpMode", "serviceHost", "servicePort", "serviceStatsPort", "serviceName", "serviceInstallStatus", "serviceInstallationMessage", "runningMode", "serviceConfigurationFailed", "cgConfigurationId", ], str]):
                return super().get_item_oapg(name)
            
        
            def __new__(
                cls,
                *_args: typing.Union[dict, frozendict.frozendict, ],
                airwatchComponentsInstalled: typing.Union[MetaOapg.properties.airwatchComponentsInstalled, str, ],
                apiServerUsername: typing.Union[MetaOapg.properties.apiServerUsername, str, ],
                organizationGroupCode: typing.Union[MetaOapg.properties.organizationGroupCode, str, ],
                apiServerUrl: typing.Union[MetaOapg.properties.apiServerUrl, str, ],
                apiServerPassword: typing.Union[MetaOapg.properties.apiServerPassword, str, ],
                airwatchServerHostname: typing.Union[MetaOapg.properties.airwatchServerHostname, str, ],
                reinitializeGatewayProcess: typing.Union[MetaOapg.properties.reinitializeGatewayProcess, bool, schemas.Unset] = schemas.unset,
                outboundProxyHost: typing.Union[MetaOapg.properties.outboundProxyHost, str, schemas.Unset] = schemas.unset,
                outboundProxyPort: typing.Union[MetaOapg.properties.outboundProxyPort, str, schemas.Unset] = schemas.unset,
                outboundProxyUsername: typing.Union[MetaOapg.properties.outboundProxyUsername, str, schemas.Unset] = schemas.unset,
                ntlmAuthentication: typing.Union[MetaOapg.properties.ntlmAuthentication, bool, schemas.Unset] = schemas.unset,
                outboundProxyPassword: typing.Union[MetaOapg.properties.outboundProxyPassword, str, schemas.Unset] = schemas.unset,
                airwatchOutboundProxy: typing.Union[MetaOapg.properties.airwatchOutboundProxy, bool, schemas.Unset] = schemas.unset,
                airwatchAgentStartUpMode: typing.Union[MetaOapg.properties.airwatchAgentStartUpMode, str, schemas.Unset] = schemas.unset,
                serviceHost: typing.Union[MetaOapg.properties.serviceHost, str, schemas.Unset] = schemas.unset,
                servicePort: typing.Union[MetaOapg.properties.servicePort, str, schemas.Unset] = schemas.unset,
                serviceStatsPort: typing.Union[MetaOapg.properties.serviceStatsPort, str, schemas.Unset] = schemas.unset,
                serviceName: typing.Union[MetaOapg.properties.serviceName, str, schemas.Unset] = schemas.unset,
                serviceInstallStatus: typing.Union[MetaOapg.properties.serviceInstallStatus, bool, schemas.Unset] = schemas.unset,
                serviceInstallationMessage: typing.Union[MetaOapg.properties.serviceInstallationMessage, str, schemas.Unset] = schemas.unset,
                runningMode: typing.Union[MetaOapg.properties.runningMode, str, schemas.Unset] = schemas.unset,
                serviceConfigurationFailed: typing.Union[MetaOapg.properties.serviceConfigurationFailed, bool, schemas.Unset] = schemas.unset,
                cgConfigurationId: typing.Union[MetaOapg.properties.cgConfigurationId, str, schemas.Unset] = schemas.unset,
                _configuration: typing.Optional[schemas.Configuration] = None,
                **kwargs: typing.Union[schemas.AnyTypeSchema, dict, frozendict.frozendict, str, date, datetime, uuid.UUID, int, float, decimal.Decimal, None, list, tuple, bytes],
            ) -> 'all_of_1': # noqa: F821
                return super().__new__(
                    cls,
                    *_args,
                    airwatchComponentsInstalled=airwatchComponentsInstalled,
                    apiServerUsername=apiServerUsername,
                    organizationGroupCode=organizationGroupCode,
                    apiServerUrl=apiServerUrl,
                    apiServerPassword=apiServerPassword,
                    airwatchServerHostname=airwatchServerHostname,
                    reinitializeGatewayProcess=reinitializeGatewayProcess,
                    outboundProxyHost=outboundProxyHost,
                    outboundProxyPort=outboundProxyPort,
                    outboundProxyUsername=outboundProxyUsername,
                    ntlmAuthentication=ntlmAuthentication,
                    outboundProxyPassword=outboundProxyPassword,
                    airwatchOutboundProxy=airwatchOutboundProxy,
                    airwatchAgentStartUpMode=airwatchAgentStartUpMode,
                    serviceHost=serviceHost,
                    servicePort=servicePort,
                    serviceStatsPort=serviceStatsPort,
                    serviceName=serviceName,
                    serviceInstallStatus=serviceInstallStatus,
                    serviceInstallationMessage=serviceInstallationMessage,
                    runningMode=runningMode,
                    serviceConfigurationFailed=serviceConfigurationFailed,
                    cgConfigurationId=cgConfigurationId,
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
                EdgeServiceSettings,
                cls.all_of_1,
            ]


    def __new__(
        cls,
        *_args: typing.Union[dict, frozendict.frozendict, str, date, datetime, uuid.UUID, int, float, decimal.Decimal, bool, None, list, tuple, bytes, io.FileIO, io.BufferedReader, ],
        _configuration: typing.Optional[schemas.Configuration] = None,
        **kwargs: typing.Union[schemas.AnyTypeSchema, dict, frozendict.frozendict, str, date, datetime, uuid.UUID, int, float, decimal.Decimal, None, list, tuple, bytes],
    ) -> 'AirWatchCGEdgeServiceSettings':
        return super().__new__(
            cls,
            *_args,
            _configuration=_configuration,
            **kwargs,
        )

from openapi_client.model.edge_service_settings import EdgeServiceSettings
