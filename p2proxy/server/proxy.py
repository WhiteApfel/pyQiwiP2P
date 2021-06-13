# from models import Referer, RequestReferer, P2ProxyError, ResponseReferer, RequestGetByUid, ResponseReferers
from app import app
from starlette.responses import RedirectResponse, HTMLResponse
import validators
import os


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


@app.get("/{bill_uid}")
async def ref_redirect(bill_uid: str):
    if validators.uuid(bill_uid):
        return RedirectResponse(
            url=f"https://vk.com/away.php?to=https://{os.environ.get('QP2P_DOMAIN', 'qp2p.0708.su')}/second/{bill_uid}",
            status_code=308,
        )
    return "Oooops"


@app.get("/second/{bill_uid}")
async def ref_redirect_qiwi(bill_uid: str):
    if validators.uuid(bill_uid):
        return RedirectResponse(
            url=f"https://oplata.qiwi.com/form?invoiceUid={bill_uid}",
            status_code=308,
        )
    return "Oooops"


@app.get("/bill/{bill_uid}")
async def ref_redirect_qiwi(bill_uid: str):
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
    return "Oooops"

