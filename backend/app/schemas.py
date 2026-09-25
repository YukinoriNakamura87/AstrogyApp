"""Compatibility exports for the public API schemas."""

from app.presentation.schemas import (
    BirthPlaceSearchResponse,
    ChartRead,
    ClientCreateRequest,
    ClientDetailResponse,
    ClientListResponse,
    ClientProfileResponse,
    DashboardResponse,
)

ClientCreate = ClientCreateRequest
ClientRead = ClientDetailResponse

__all__ = [
    "ChartRead", "ClientCreate", "ClientCreateRequest", "ClientDetailResponse",
    "BirthPlaceSearchResponse", "ClientListResponse", "ClientProfileResponse", "ClientRead", "DashboardResponse",
]
