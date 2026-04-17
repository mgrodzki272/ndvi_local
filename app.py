from io import BytesIO
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, Response
from rasterio.io import MemoryFile

matplotlib.use("Agg")

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    return HTMLResponse((Path(__file__).resolve().parent / "web/index.html").read_text())


@app.post("/api/ndvi")
async def api_ndvi(red: UploadFile = File(...), nir: UploadFile = File(...)) -> Response:
    with MemoryFile(await red.read()) as rmem, MemoryFile(await nir.read()) as nmem:
        with rmem.open() as rsrc, nmem.open() as nsrc:
            red_arr = rsrc.read(1).astype("float32")
            nir_arr = nsrc.read(1).astype("float32")

    denom = nir_arr + red_arr
    ndvi_arr = np.where(denom == 0, np.nan, (nir_arr - red_arr) / denom)

    fig = plt.figure(figsize=(7, 5), dpi=160)
    ax = fig.add_subplot(1, 1, 1)
    im = ax.imshow(ndvi_arr, cmap="RdYlGn", vmin=-1, vmax=1)
    fig.colorbar(im, ax=ax, label="NDVI")
    ax.set_axis_off()
    fig.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)

    return Response(content=buf.getvalue(), media_type="image/png")
