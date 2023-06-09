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


class WsPortalEdgeServiceSettings(
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
                    "instanceId",
                    "proxyPattern",
                }
                
                class properties:
                    
                    
                    class instanceId(
                        schemas.StrSchema
                    ):
                    
                    
                        class MetaOapg:
                            regex=[{
                                'pattern': r'^(?!.*\/\/).*',  # noqa: E501
                            }]
                    externalUrl = schemas.StrSchema
                    proxyPattern = schemas.StrSchema
                    unSecurePattern = schemas.StrSchema
                    authCookie = schemas.StrSchema
                    loginRedirectURL = schemas.StrSchema
                    proxyHostPattern = schemas.StrSchema
                    keyTabPrincipalName = schemas.StrSchema
                    targetSPN = schemas.StrSchema
                    keyTabFilePath = schemas.StrSchema
                    idpEntityID = schemas.StrSchema
                    allowedAudiences = schemas.StrSchema
                    landingPagePath = schemas.StrSchema
                    userNameHeader = schemas.StrSchema
                    
                    
                    class wrpAuthConsumeType(
                        schemas.EnumBase,
                        schemas.StrSchema
                    ):
                    
                    
                        class MetaOapg:
                            enum_value_to_name = {
                                "SAML": "SAML",
                                "CERTIFICATE": "CERTIFICATE",
                            }
                        
                        @schemas.classproperty
                        def SAML(cls):
                            return cls("SAML")
                        
                        @schemas.classproperty
                        def CERTIFICATE(cls):
                            return cls("CERTIFICATE")
                    keyTabRealm = schemas.StrSchema
                    
                    
                    class samlAttributeHeaderMap(
                        schemas.DictSchema
                    ):
                    
                    
                        class MetaOapg:
                            additional_properties = schemas.StrSchema
                        
                        def __getitem__(self, name: typing.Union[str, ]) -> MetaOapg.additional_properties:
                            # dict_instance[name] accessor
                            return super().__getitem__(name)
                        
                        def get_item_oapg(self, name: typing.Union[str, ]) -> MetaOapg.additional_properties:
                            return super().get_item_oapg(name)
                    
                        def __new__(
                            cls,
                            *_args: typing.Union[dict, frozendict.frozendict, ],
                            _configuration: typing.Optional[schemas.Configuration] = None,
                            **kwargs: typing.Union[MetaOapg.additional_properties, str, ],
                        ) -> 'samlAttributeHeaderMap':
                            return super().__new__(
                                cls,
                                *_args,
                                _configuration=_configuration,
                                **kwargs,
                            )
                    
                    
                    class securityHeaders(
                        schemas.DictSchema
                    ):
                    
                    
                        class MetaOapg:
                            additional_properties = schemas.StrSchema
                        
                        def __getitem__(self, name: typing.Union[str, ]) -> MetaOapg.additional_properties:
                            # dict_instance[name] accessor
                            return super().__getitem__(name)
                        
                        def get_item_oapg(self, name: typing.Union[str, ]) -> MetaOapg.additional_properties:
                            return super().get_item_oapg(name)
                    
                        def __new__(
                            cls,
                            *_args: typing.Union[dict, frozendict.frozendict, ],
                            _configuration: typing.Optional[schemas.Configuration] = None,
                            **kwargs: typing.Union[MetaOapg.additional_properties, str, ],
                        ) -> 'securityHeaders':
                            return super().__new__(
                                cls,
                                *_args,
                                _configuration=_configuration,
                                **kwargs,
                            )
                    __annotations__ = {
                        "instanceId": instanceId,
                        "externalUrl": externalUrl,
                        "proxyPattern": proxyPattern,
                        "unSecurePattern": unSecurePattern,
                        "authCookie": authCookie,
                        "loginRedirectURL": loginRedirectURL,
                        "proxyHostPattern": proxyHostPattern,
                        "keyTabPrincipalName": keyTabPrincipalName,
                        "targetSPN": targetSPN,
                        "keyTabFilePath": keyTabFilePath,
                        "idpEntityID": idpEntityID,
                        "allowedAudiences": allowedAudiences,
                        "landingPagePath": landingPagePath,
                        "userNameHeader": userNameHeader,
                        "wrpAuthConsumeType": wrpAuthConsumeType,
                        "keyTabRealm": keyTabRealm,
                        "samlAttributeHeaderMap": samlAttributeHeaderMap,
                        "securityHeaders": securityHeaders,
                    }
            
            instanceId: MetaOapg.properties.instanceId
            proxyPattern: MetaOapg.properties.proxyPattern
            
            @typing.overload
            def __getitem__(self, name: typing_extensions.Literal["instanceId"]) -> MetaOapg.properties.instanceId: ...
            
            @typing.overload
            def __getitem__(self, name: typing_extensions.Literal["externalUrl"]) -> MetaOapg.properties.externalUrl: ...
            
            @typing.overload
            def __getitem__(self, name: typing_extensions.Literal["proxyPattern"]) -> MetaOapg.properties.proxyPattern: ...
            
            @typing.overload
            def __getitem__(self, name: typing_extensions.Literal["unSecurePattern"]) -> MetaOapg.properties.unSecurePattern: ...
            
            @typing.overload
            def __getitem__(self, name: typing_extensions.Literal["authCookie"]) -> MetaOapg.properties.authCookie: ...
            
            @typing.overload
            def __getitem__(self, name: typing_extensions.Literal["loginRedirectURL"]) -> MetaOapg.properties.loginRedirectURL: ...
            
            @typing.overload
            def __getitem__(self, name: typing_extensions.Literal["proxyHostPattern"]) -> MetaOapg.properties.proxyHostPattern: ...
            
            @typing.overload
            def __getitem__(self, name: typing_extensions.Literal["keyTabPrincipalName"]) -> MetaOapg.properties.keyTabPrincipalName: ...
            
            @typing.overload
            def __getitem__(self, name: typing_extensions.Literal["targetSPN"]) -> MetaOapg.properties.targetSPN: ...
            
            @typing.overload
            def __getitem__(self, name: typing_extensions.Literal["keyTabFilePath"]) -> MetaOapg.properties.keyTabFilePath: ...
            
            @typing.overload
            def __getitem__(self, name: typing_extensions.Literal["idpEntityID"]) -> MetaOapg.properties.idpEntityID: ...
            
            @typing.overload
            def __getitem__(self, name: typing_extensions.Literal["allowedAudiences"]) -> MetaOapg.properties.allowedAudiences: ...
            
            @typing.overload
            def __getitem__(self, name: typing_extensions.Literal["landingPagePath"]) -> MetaOapg.properties.landingPagePath: ...
            
            @typing.overload
            def __getitem__(self, name: typing_extensions.Literal["userNameHeader"]) -> MetaOapg.properties.userNameHeader: ...
            
            @typing.overload
            def __getitem__(self, name: typing_extensions.Literal["wrpAuthConsumeType"]) -> MetaOapg.properties.wrpAuthConsumeType: ...
            
            @typing.overload
            def __getitem__(self, name: typing_extensions.Literal["keyTabRealm"]) -> MetaOapg.properties.keyTabRealm: ...
            
            @typing.overload
            def __getitem__(self, name: typing_extensions.Literal["samlAttributeHeaderMap"]) -> MetaOapg.properties.samlAttributeHeaderMap: ...
            
            @typing.overload
            def __getitem__(self, name: typing_extensions.Literal["securityHeaders"]) -> MetaOapg.properties.securityHeaders: ...
            
            @typing.overload
            def __getitem__(self, name: str) -> schemas.UnsetAnyTypeSchema: ...
            
            def __getitem__(self, name: typing.Union[typing_extensions.Literal["instanceId", "externalUrl", "proxyPattern", "unSecurePattern", "authCookie", "loginRedirectURL", "proxyHostPattern", "keyTabPrincipalName", "targetSPN", "keyTabFilePath", "idpEntityID", "allowedAudiences", "landingPagePath", "userNameHeader", "wrpAuthConsumeType", "keyTabRealm", "samlAttributeHeaderMap", "securityHeaders", ], str]):
                # dict_instance[name] accessor
                return super().__getitem__(name)
            
            
            @typing.overload
            def get_item_oapg(self, name: typing_extensions.Literal["instanceId"]) -> MetaOapg.properties.instanceId: ...
            
            @typing.overload
            def get_item_oapg(self, name: typing_extensions.Literal["externalUrl"]) -> typing.Union[MetaOapg.properties.externalUrl, schemas.Unset]: ...
            
            @typing.overload
            def get_item_oapg(self, name: typing_extensions.Literal["proxyPattern"]) -> MetaOapg.properties.proxyPattern: ...
            
            @typing.overload
            def get_item_oapg(self, name: typing_extensions.Literal["unSecurePattern"]) -> typing.Union[MetaOapg.properties.unSecurePattern, schemas.Unset]: ...
            
            @typing.overload
            def get_item_oapg(self, name: typing_extensions.Literal["authCookie"]) -> typing.Union[MetaOapg.properties.authCookie, schemas.Unset]: ...
            
            @typing.overload
            def get_item_oapg(self, name: typing_extensions.Literal["loginRedirectURL"]) -> typing.Union[MetaOapg.properties.loginRedirectURL, schemas.Unset]: ...
            
            @typing.overload
            def get_item_oapg(self, name: typing_extensions.Literal["proxyHostPattern"]) -> typing.Union[MetaOapg.properties.proxyHostPattern, schemas.Unset]: ...
            
            @typing.overload
            def get_item_oapg(self, name: typing_extensions.Literal["keyTabPrincipalName"]) -> typing.Union[MetaOapg.properties.keyTabPrincipalName, schemas.Unset]: ...
            
            @typing.overload
            def get_item_oapg(self, name: typing_extensions.Literal["targetSPN"]) -> typing.Union[MetaOapg.properties.targetSPN, schemas.Unset]: ...
            
            @typing.overload
            def get_item_oapg(self, name: typing_extensions.Literal["keyTabFilePath"]) -> typing.Union[MetaOapg.properties.keyTabFilePath, schemas.Unset]: ...
            
            @typing.overload
            def get_item_oapg(self, name: typing_extensions.Literal["idpEntityID"]) -> typing.Union[MetaOapg.properties.idpEntityID, schemas.Unset]: ...
            
            @typing.overload
            def get_item_oapg(self, name: typing_extensions.Literal["allowedAudiences"]) -> typing.Union[MetaOapg.properties.allowedAudiences, schemas.Unset]: ...
            
            @typing.overload
            def get_item_oapg(self, name: typing_extensions.Literal["landingPagePath"]) -> typing.Union[MetaOapg.properties.landingPagePath, schemas.Unset]: ...
            
            @typing.overload
            def get_item_oapg(self, name: typing_extensions.Literal["userNameHeader"]) -> typing.Union[MetaOapg.properties.userNameHeader, schemas.Unset]: ...
            
            @typing.overload
            def get_item_oapg(self, name: typing_extensions.Literal["wrpAuthConsumeType"]) -> typing.Union[MetaOapg.properties.wrpAuthConsumeType, schemas.Unset]: ...
            
            @typing.overload
            def get_item_oapg(self, name: typing_extensions.Literal["keyTabRealm"]) -> typing.Union[MetaOapg.properties.keyTabRealm, schemas.Unset]: ...
            
            @typing.overload
            def get_item_oapg(self, name: typing_extensions.Literal["samlAttributeHeaderMap"]) -> typing.Union[MetaOapg.properties.samlAttributeHeaderMap, schemas.Unset]: ...
            
            @typing.overload
            def get_item_oapg(self, name: typing_extensions.Literal["securityHeaders"]) -> typing.Union[MetaOapg.properties.securityHeaders, schemas.Unset]: ...
            
            @typing.overload
            def get_item_oapg(self, name: str) -> typing.Union[schemas.UnsetAnyTypeSchema, schemas.Unset]: ...
            
            def get_item_oapg(self, name: typing.Union[typing_extensions.Literal["instanceId", "externalUrl", "proxyPattern", "unSecurePattern", "authCookie", "loginRedirectURL", "proxyHostPattern", "keyTabPrincipalName", "targetSPN", "keyTabFilePath", "idpEntityID", "allowedAudiences", "landingPagePath", "userNameHeader", "wrpAuthConsumeType", "keyTabRealm", "samlAttributeHeaderMap", "securityHeaders", ], str]):
                return super().get_item_oapg(name)
            
        
            def __new__(
                cls,
                *_args: typing.Union[dict, frozendict.frozendict, ],
                instanceId: typing.Union[MetaOapg.properties.instanceId, str, ],
                proxyPattern: typing.Union[MetaOapg.properties.proxyPattern, str, ],
                externalUrl: typing.Union[MetaOapg.properties.externalUrl, str, schemas.Unset] = schemas.unset,
                unSecurePattern: typing.Union[MetaOapg.properties.unSecurePattern, str, schemas.Unset] = schemas.unset,
                authCookie: typing.Union[MetaOapg.properties.authCookie, str, schemas.Unset] = schemas.unset,
                loginRedirectURL: typing.Union[MetaOapg.properties.loginRedirectURL, str, schemas.Unset] = schemas.unset,
                proxyHostPattern: typing.Union[MetaOapg.properties.proxyHostPattern, str, schemas.Unset] = schemas.unset,
                keyTabPrincipalName: typing.Union[MetaOapg.properties.keyTabPrincipalName, str, schemas.Unset] = schemas.unset,
                targetSPN: typing.Union[MetaOapg.properties.targetSPN, str, schemas.Unset] = schemas.unset,
                keyTabFilePath: typing.Union[MetaOapg.properties.keyTabFilePath, str, schemas.Unset] = schemas.unset,
                idpEntityID: typing.Union[MetaOapg.properties.idpEntityID, str, schemas.Unset] = schemas.unset,
                allowedAudiences: typing.Union[MetaOapg.properties.allowedAudiences, str, schemas.Unset] = schemas.unset,
                landingPagePath: typing.Union[MetaOapg.properties.landingPagePath, str, schemas.Unset] = schemas.unset,
                userNameHeader: typing.Union[MetaOapg.properties.userNameHeader, str, schemas.Unset] = schemas.unset,
                wrpAuthConsumeType: typing.Union[MetaOapg.properties.wrpAuthConsumeType, str, schemas.Unset] = schemas.unset,
                keyTabRealm: typing.Union[MetaOapg.properties.keyTabRealm, str, schemas.Unset] = schemas.unset,
                samlAttributeHeaderMap: typing.Union[MetaOapg.properties.samlAttributeHeaderMap, dict, frozendict.frozendict, schemas.Unset] = schemas.unset,
                securityHeaders: typing.Union[MetaOapg.properties.securityHeaders, dict, frozendict.frozendict, schemas.Unset] = schemas.unset,
                _configuration: typing.Optional[schemas.Configuration] = None,
                **kwargs: typing.Union[schemas.AnyTypeSchema, dict, frozendict.frozendict, str, date, datetime, uuid.UUID, int, float, decimal.Decimal, None, list, tuple, bytes],
            ) -> 'all_of_1':
                return super().__new__(
                    cls,
                    *_args,
                    instanceId=instanceId,
                    proxyPattern=proxyPattern,
                    externalUrl=externalUrl,
                    unSecurePattern=unSecurePattern,
                    authCookie=authCookie,
                    loginRedirectURL=loginRedirectURL,
                    proxyHostPattern=proxyHostPattern,
                    keyTabPrincipalName=keyTabPrincipalName,
                    targetSPN=targetSPN,
                    keyTabFilePath=keyTabFilePath,
                    idpEntityID=idpEntityID,
                    allowedAudiences=allowedAudiences,
                    landingPagePath=landingPagePath,
                    userNameHeader=userNameHeader,
                    wrpAuthConsumeType=wrpAuthConsumeType,
                    keyTabRealm=keyTabRealm,
                    samlAttributeHeaderMap=samlAttributeHeaderMap,
                    securityHeaders=securityHeaders,
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
    ) -> 'WsPortalEdgeServiceSettings':
        return super().__new__(
            cls,
            *_args,
            _configuration=_configuration,
            **kwargs,
        )

from openapi_client.model.edge_service_settings import EdgeServiceSettings
