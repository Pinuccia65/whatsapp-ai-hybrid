"""
Tenant Service.

Gestisce la configurazione dei tenant:
- CRUD operazioni
- Ricerca per WhatsApp phone number ID
- Validazione configurazione
"""

from typing import Optional, List
from app.models.tenant import TenantModel, Tenant
from app.schemas.tenant import TenantCreate, TenantUpdate


class TenantService:
    """Servizio per gestione tenant."""
    
    async def list_tenants(self) -> List[Tenant]:
        """Lista tutti i tenant."""
        tenants = await TenantModel.find_all().to_list()
        return [t.to_dict() for t in tenants]
    
    async def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Ottieni tenant per ID."""
        tenant = await TenantModel.find_one(TenantModel.id == tenant_id)
        return tenant.to_dict() if tenant else None
    
    async def get_tenant_by_whatsapp_id(self, phone_number_id: str) -> Optional[Tenant]:
        """Ottieni tenant per WhatsApp phone number ID."""
        tenant = await TenantModel.find_one(
            TenantModel.whatsapp_phone_number_id == phone_number_id
        )
        return tenant.to_dict() if tenant else None
    
    async def create_tenant(self, data: TenantCreate) -> Tenant:
        """Crea un nuovo tenant."""
        # Validazione
        if not data.name:
            raise ValueError("Tenant name is required")
        if not data.whatsapp_phone_number_id:
            raise ValueError("WhatsApp phone number ID is required")
        
        # Verifica unicità phone number ID
        existing = await self.get_tenant_by_whatsapp_id(data.whatsapp_phone_number_id)
        if existing:
            raise ValueError("WhatsApp phone number ID already in use")
        
        # Crea tenant
        tenant = TenantModel(**data.dict())
        await tenant.insert()
        
        return tenant.to_dict()
    
    async def update_tenant(self, tenant_id: str, data: TenantUpdate) -> Optional[Tenant]:
        """Aggiorna un tenant."""
        tenant = await TenantModel.find_one(TenantModel.id == tenant_id)
        if not tenant:
            return None
        
        # Aggiorna solo i campi forniti
        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(tenant, key, value)
        
        await tenant.save()
        return tenant.to_dict()