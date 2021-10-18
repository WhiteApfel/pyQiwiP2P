# from models import Referer, RequestReferer, P2ProxyError, ResponseReferer, RequestGetByUid, ResponseReferers
from starlette.responses import RedirectResponse, HTMLResponse
import validators
import os

from starlette.routing import Router

router = Router()


# Это не работает, Женя просто попутал что-то...
#
# @app.get("/ref/{referer_uid}/bill/{bill_uid}")
# async def ref_redirect(referer_uid: str, bill_uid: str):
#     if validators.uuid(bill_uid):
#         if validators.uuid(referer_uid):
#             referer = Referer.get_or_none(Referer.uid == referer_uid)
#             if referer:
#                 return RedirectResponse(
#                     url=f"https://oplata.qiwi.com/form?invoiceUid={bill_uid}",
#                     status_code=308,
#                     headers={
#                         "Referer": referer.referer
#                     }
#                 )
#     return "ok"


@router.route("/{bill_uid}", "GET")
async def ref_redirect_vk(bill_uid: str):
    if validators.uuid(bill_uid):
        return RedirectResponse(
            url=f"https://vk.com/away.php?to=https://{os.environ.get('QP2P_DOMAIN', 'qp2p.0708.su')}/second/{bill_uid}",
            status_code=308,
        )
    return HTMLResponse("<body><h1>Invalid bill_id</h1></body>")


@router.route("/second/{bill_uid}", "GET")
async def ref_redirect_qiwi(bill_uid: str):
    if validators.uuid(bill_uid):
        return RedirectResponse(
            url=f"https://oplata.qiwi.com/form?invoiceUid={bill_uid}",
            status_code=308,
        )
    return HTMLResponse("<body><h1>Invalid bill_id</h1></body>")


@router.route("/bill/{bill_uid}", "GET")
async def ref_redirect_qiwi_bill(bill_uid: str):
    if validators.uuid(bill_uid):
        # return RedirectResponse(
        #     url=f"https://oplata.qiwi.com/form?invoiceUid={bill_uid}",
        #     status_code=308,
        # )
        return HTMLResponse(
            f"""
                <script>
                    location.href = "https://oplata.qiwi.com/form?invoiceUid={bill_uid}"
                </script>
            """
        )
    return HTMLResponse("<body><h1>Invalid bill_id</h1></body>")


@router.route("/", "GET")
async def index():
    return RedirectResponse(
        url=f"https://github.com/WhiteApfel/pyQiwiP2P",
        status_code=307,
    )
