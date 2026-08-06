import subprocess
import tempfile
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

app = FastAPI()


class CompileRequest(BaseModel):
    tex: str


@app.post("/compile")
def compile_latex(request: CompileRequest):
    with tempfile.TemporaryDirectory() as tmpdir:
        tex_path = Path(tmpdir) / "documento.tex"
        tex_path.write_text(request.tex, encoding="utf-8")

        result = None
        for _ in range(2):  # duas passadas: resolve sumário/referências do hyperref
            result = subprocess.run(
                [
                    "pdflatex",
                    "-interaction=nonstopmode",
                    "-halt-on-error",
                    "-output-directory",
                    tmpdir,
                    str(tex_path),
                ],
                cwd=tmpdir,
                capture_output=True,
                text=True,
                timeout=60,
            )

        pdf_path = Path(tmpdir) / "documento.pdf"
        if result.returncode != 0 or not pdf_path.exists():
            raise HTTPException(status_code=422, detail=result.stdout[-4000:])

        return Response(content=pdf_path.read_bytes(), media_type="application/pdf")


@app.get("/health")
def health():
    return {"status": "ok"}
