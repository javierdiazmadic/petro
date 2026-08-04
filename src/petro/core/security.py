"""Security utilities for Petro application."""

from typing import List

from fastapi.middleware.cors import CORSMiddleware


def setup_cors(app, origins: List[str]) -> None:
    """Setup CORS middleware.

    Args:
        app: FastAPI application instance
        origins: List of allowed origins
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
