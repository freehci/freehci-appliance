from openapi_client.paths.v1_config_proxy.get import ApiForget
from openapi_client.paths.v1_config_proxy.put import ApiForput
from openapi_client.paths.v1_config_proxy.post import ApiForpost


class V1ConfigProxy(
    ApiForget,
    ApiForput,
    ApiForpost,
):
    pass
