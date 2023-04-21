from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .middlewares import CheckAPIKeyMiddleware, ExceptionHandlingMiddleware
from .routers import erc20_txns_details_router

app = FastAPI()

# Register middlewares
# app.add_middleware(CheckAPIKeyMiddleware) # TODO: Uncomment this line when API key is integrated
app.add_middleware(ExceptionHandlingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(erc20_txns_details_router.router, prefix="/api/ethereum/erc20")
