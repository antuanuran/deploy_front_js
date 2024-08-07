from fastapi import FastAPI
import uvicorn
import logging
import routers

from configs import COMMON


logging.basicConfig(format="%(asctime)s|%(levelname)s|%(message)s", level="INFO")
logger = logging.getLogger(__name__)


app = FastAPI()
app.include_router(routers.router)

if __name__ == "__main__":

    uvicorn.run(
        "main:app", host="0.0.0.0", port=COMMON.port_for_onvif, reload=False, server_header=False
    )

    logging.info(" main | __main__ | uvicorn start \n ")
