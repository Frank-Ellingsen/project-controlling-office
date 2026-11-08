import os
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

app = FastAPI(
    title='Elkem Project Controlling Office API',
    description='Agentic Financial Control & Project Reporting Platform',
    version='1.0.0'
)

class EVMRequest(BaseModel):
    control_account_id: str = Field(..., example='CA-1042')
    bac: float = Field(..., gt=0, example=10000000.0)
    bcws: float = Field(..., ge=0, example=4000000.0)
    bcwp: float = Field(..., ge=0, example=3500000.0)
    acwp: float = Field(..., ge=0, example=3800000.0)

@app.get('/')
def root():
    return {'status': 'healthy', 'service': 'Elkem Project Controlling API'}

@app.post('/api/v1/evm/calculate')
def calculate_evm(req: EVMRequest):
    cpi = round(req.bcwp / req.acwp, 4) if req.acwp > 0 else 1.0
    spi = round(req.bcwp / req.bcws, 4) if req.bcws > 0 else 1.0
    eac = round(req.bac / cpi, 2) if cpi > 0 else req.bac
    return {
        'control_account_id': req.control_account_id,
        'cpi': cpi,
        'spi': spi,
        'eac': eac
    }

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
