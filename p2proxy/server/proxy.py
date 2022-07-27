import os

import validators
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.routing import Router, Route

router = Router()


async def ref_redirect_vk(request: Request):
    if validators.uuid(request.path_params["bill_id"]):
        return RedirectResponse(
            url=f"https://vk.com/away.php?to=https://{os.environ.get('QP2P_DOMAIN', 'qp2p.0708.su')}/second/{request.path_params['bill_uid']}",
            status_code=308,
        )
    return HTMLResponse("<body><h1>Invalid bill_id</h1></body>")


async def ref_redirect_qiwi(request: Request):
    if validators.uuid(request.path_params["bill_uid"]):
        return RedirectResponse(
            url=f"https://oplata.qiwi.com/form?invoiceUid={request.path_params['bill_uid']}",
            status_code=308,
        )
    return HTMLResponse("<body><h1>Invalid bill_id</h1></body>")


async def ref_redirect_qiwi_bill(request: Request):
    if validators.uuid(request.path_params["bill_uid"]):
        return HTMLResponse(
            f"""
                <script>
                    location.href = "https://oplata.qiwi.com/form?invoiceUid={request.path_params['bill_uid']}"
                </script>
            """
        )
    return HTMLResponse("<body><h1>Invalid bill_id</h1></body>")


async def index(request: Request):
    return RedirectResponse(
        url=f"https://github.com/WhiteApfel/pyQiwiP2P",
        status_code=307,
    )


routes = [
    Route("/", index),
    Route("/{bill_uid}", ref_redirect_vk, methods=["GET"]),
    Route("/second/{bill_uid}", ref_redirect_qiwi, methods=["GET"]),
    Route("/bill/{bill_uid}", ref_redirect_qiwi_bill, methods=["GET"]),
]
