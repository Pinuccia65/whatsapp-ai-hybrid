"""
Tenants Routes.

Endpoint per gestire la configurazione dei tenant:
- Lista tutti i tenant
- Ottieni tenant per ID
- Ottieni tenant per WhatsApp phone number ID
- Crea nuovo tenant
- Aggiorna tenant
"""

from typing import List
from fastapi import APIRouter, HTTPException

from app.schemas.tenant import Tenant, TenantCreate, TenantUpdate
from app.services.tenant_service import TenantService

router = APIRouter()
service = TenantService()


@router.get("/", response_model=List[Tenant])
async def list_tenants():
    """Lista tutti i tenant."""
    try:
        tenants = await service.list_tenants()
        return tenants
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{tenant_id}", response_model=Tenant)
async def get_tenant(tenant_id: str):
    """Ottieni un tenant per ID."""
    tenant = await service.get_tenant(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant


@router.get("/whatsapp/{phone_number_id}", response_model=Tenant)
async def get_tenant_by_whatsapp(phone_number_id: str):
    """Ottieni tenant per WhatsApp phone number ID."""
    tenant = await service.get_tenant_by_whatsapp_id(phone_number_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant


@router.post("/", response_model=Tenant, status_code=201)
async def create_tenant(tenant: TenantCreate):
    """Crea un nuovo tenant."""
    try:
        created = await service.create_tenant(tenant)
        return created
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{tenant_id}", response_model=Tenant)
async def update_tenant(tenant_id: str, tenant: TenantUpdate):
    """Aggiorna un tenant."""
    try:
        updated = await service.update_tenant(tenant_id, tenant)
        if not updated:
            raise HTTPException(status_code=404, detail="Tenant not found")
        return updated
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))