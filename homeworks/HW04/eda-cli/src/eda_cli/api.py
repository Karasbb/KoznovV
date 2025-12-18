app = FastAPI(), /health, /quality, /quality-from-csv
from fastapi import FastAPI, HTTPException, UploadFile
from pydantic import BaseModel
import pandas as pd
from pathlib import Path
from time import perf_counter
from .core import summarize_dataset, missing_table, compute_quality_flags

app = FastAPI(title="EDA CLI Service")

class QualityRequest(BaseModel):
    n_rows: int
    n_cols: int
    max_missing_share: float
    numeric_cols: int
    categorical_cols: int

class QualityResponse(BaseModel):
    ok_for_model: bool
    quality_score: float
    message: str
    latency_ms: float
    flags: dict
    dataset_shape: dict

@app.get("/health")
def health():
    return {"status": "ok", "service": "eda-cli", "version": "0.1.0"}

@app.post("/quality", response_model=QualityResponse)
def quality(request: QualityRequest):
    start = perf_counter()
     
    flags = {
        "too_few_rows": request.n_rows < 100,
        "too_many_missing": request.max_missing_share > 0.5,
        "has_constant_columns": False  
    }
    score = 1.0 - request.max_missing_share
    latency = (perf_counter() - start) * 1000
    return QualityResponse(ok_for_model=score > 0.5, quality_score=score, message="OK", latency_ms=latency, flags=flags, dataset_shape={"rows": request.n_rows, "cols": request.n_cols})

@app.post("/quality-from-csv")
def quality_from_csv(file: UploadFile):
    start = perf_counter()
    try:
        df = pd.read_csv(file.file)
    except:
        raise HTTPException(400, "Invalid CSV")
    summary = summarize_dataset(df)
    missing_df = missing_table(df)
    flags = compute_quality_flags(summary, missing_df)
    score = flags["quality_score"]
    latency = (perf_counter() - start) * 1000
    return {"ok_for_model": score > 0.5, "quality_score": score, "message": "OK", "latency_ms": latency, "flags": flags, "dataset_shape": {"rows": len(df), "cols": len(df.columns)}}