"""Tenants Routes."""

from typing import List
from fastapi import APIRouter, HTTPException

from app.schemas.tenant import Tenant, TenantCreate, TenantUpdate
from app.services.tenant_service import TenantService

router = APIRouter()
service = TenantService()


@router.get("/", response_model=List[dict])
async def list_tenants():
    return await service.list_tenants()


@router.get("/{tenant_id}", response_model=dict)
async def get_tenant(tenant_id: str):
    tenant = await service.get_tenant(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Not found")
    return tenant


@router.get("/whatsapp/{phone_number_id}", response_model=dict)
async def get_tenant_by_whatsapp(phone_number_id: str):
    tenant = await service.get_tenant_by_whatsapp_id(phone_number_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Not found")
    return tenant


@router.post("/", status_code=201)
async def create_tenant(tenant: TenantCreate):
    try:
        return await service.create_tenant(tenant.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{tenant_id}")
async def update_tenant(tenant_id: str, tenant: TenantUpdate):
    updated = await service.update_tenant(tenant_id, tenant.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Not found")
    return updated