"""Servicekatalog: maler, plan, kjøring og instanser."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.catalog import (
    ServiceDeploymentCreate,
    ServiceDeploymentRead,
    ServiceInstanceRead,
    ServiceTemplateCreate,
    ServiceTemplateRead,
    ServiceTemplateVersionCreate,
    ServiceTemplateVersionRead,
)
from app.services import catalog as cat_svc

router = APIRouter(prefix="/service-catalog", tags=["service-catalog"])


@router.get("/templates", response_model=list[ServiceTemplateRead])
def list_templates(db: Session = Depends(get_db)) -> list[ServiceTemplateRead]:
    return [cat_svc.template_to_read(r) for r in cat_svc.list_templates(db)]


@router.post("/templates", response_model=ServiceTemplateRead)
def create_template(data: ServiceTemplateCreate, db: Session = Depends(get_db)) -> ServiceTemplateRead:
    return cat_svc.template_to_read(cat_svc.create_template(db, data))


@router.get("/templates/{template_id}", response_model=ServiceTemplateRead)
def get_template(template_id: int, db: Session = Depends(get_db)) -> ServiceTemplateRead:
    row = cat_svc.get_template(db, template_id)
    if row is None:
        raise HTTPException(status_code=404, detail="mal ikke funnet")
    return cat_svc.template_to_read(row)


@router.post("/templates/{template_id}/versions", response_model=ServiceTemplateVersionRead)
def add_version(
    template_id: int,
    data: ServiceTemplateVersionCreate,
    db: Session = Depends(get_db),
) -> ServiceTemplateVersionRead:
    row = cat_svc.get_template(db, template_id)
    if row is None:
        raise HTTPException(status_code=404, detail="mal ikke funnet")
    return cat_svc.version_to_read(cat_svc.add_version(db, row, data))


@router.get("/deployments", response_model=list[ServiceDeploymentRead])
def list_deployments(db: Session = Depends(get_db)) -> list[ServiceDeploymentRead]:
    return [cat_svc.deployment_to_read(db, r) for r in cat_svc.list_deployments(db)]


@router.post("/deployments", response_model=ServiceDeploymentRead)
def create_deployment(data: ServiceDeploymentCreate, db: Session = Depends(get_db)) -> ServiceDeploymentRead:
    return cat_svc.deployment_to_read(db, cat_svc.create_deployment(db, data))


@router.get("/deployments/{deployment_id}", response_model=ServiceDeploymentRead)
def get_deployment(deployment_id: int, db: Session = Depends(get_db)) -> ServiceDeploymentRead:
    row = cat_svc.get_deployment(db, deployment_id)
    if row is None:
        raise HTTPException(status_code=404, detail="deployment ikke funnet")
    return cat_svc.deployment_to_read(db, row)


@router.post("/deployments/{deployment_id}/run", response_model=ServiceDeploymentRead)
def run_deployment(deployment_id: int, db: Session = Depends(get_db)) -> ServiceDeploymentRead:
    row = cat_svc.get_deployment(db, deployment_id)
    if row is None:
        raise HTTPException(status_code=404, detail="deployment ikke funnet")
    return cat_svc.deployment_to_read(db, cat_svc.run_deployment(db, row))


@router.get("/instances", response_model=list[ServiceInstanceRead])
def list_instances(db: Session = Depends(get_db)) -> list[ServiceInstanceRead]:
    return [cat_svc.instance_to_read(r) for r in cat_svc.list_instances(db)]
