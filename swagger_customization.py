#
# file: swagger_customization.py
#

from fastapi.openapi.docs import get_swagger_ui_html
from starlette.requests import Request

async def swagger_ui_html(request: Request):  # Add 'request' parameter here
    return get_swagger_ui_html(
        openapi_url=request.url_for("get_openapi"),  # Change this line
        title="Swagger UI (Custom)",
        swagger_favicon_url="/static/img/favicon.ico",
        swagger_css_url="/static/css/swagger-ui.css"
    )
