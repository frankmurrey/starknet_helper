from pydantic import BaseModel


class OrbiterChainData(BaseModel):
    makerAddress: str
    sender: str
    minPrice: float
    maxPrice: float
    tradingFee: float
    gasFee: float
    startTime: int
    endTime: int