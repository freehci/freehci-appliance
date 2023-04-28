# openapi_client.model.password_policy_settings.PasswordPolicySettings

## Model Type Info
Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | -------------
dict, frozendict.frozendict,  | frozendict.frozendict,  |  | 

### Dictionary Keys
Key | Input Type | Accessed Type | Description | Notes
------------ | ------------- | ------------- | ------------- | -------------
**passwordPolicyMinLen** | decimal.Decimal, int,  | decimal.Decimal,  | Minimum password Length | [optional] value must be a 32 bit integer
**passwordPolicyMinClass** | decimal.Decimal, int,  | decimal.Decimal,  | Minimum No of Character Classes | [optional] value must be a 32 bit integer
**passwordPolicyDifok** | decimal.Decimal, int,  | decimal.Decimal,  | Minimum Number of Characters different from previous | [optional] value must be a 32 bit integer
**passwordPolicyUnlockTime** | decimal.Decimal, int,  | decimal.Decimal,  | Time for which the account should stay locked | [optional] value must be a 64 bit integer
**passwordPolicyFailedLockout** | decimal.Decimal, int,  | decimal.Decimal,  | No. of attempts after which the user account should be locked | [optional] value must be a 32 bit integer
**any_string_name** | dict, frozendict.frozendict, str, date, datetime, int, float, bool, decimal.Decimal, None, list, tuple, bytes, io.FileIO, io.BufferedReader | frozendict.frozendict, str, BoolClass, decimal.Decimal, NoneClass, tuple, bytes, FileIO | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../../README.md#documentation-for-models) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to README]](../../README.md)

