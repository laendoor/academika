# Deploy y Rollback

## Flujo de deploy

1. `make release` crea un tag `vX.Y.Z` y lo pushea
2. El workflow `.github/workflows/deploy.yml` se dispara con el tag
3. Build + push de imágenes (`leandrojdl/academika-api` + `academika-ui`) a Docker Hub
4. Deploy al droplet: `pull` → `migrate` → `up`

## Migraciones

`alembic upgrade head` corre en el deploy, **antes** de `up -d`. Si falla, el deploy aborta y la versión anterior sigue corriendo (prod intacto).

## Rollback manual

Si un deploy sale mal **después** de aplicar (la migración pasó pero hay un bug):

```bash
# 1. Redeployar la imagen anterior
ssh -i ~/.ssh/id_deploy_academika deploy@157.230.87.2 \
  "cd /opt/academika && IMAGE_TAG=<version_vieja> docker compose -f compose.prod.yaml up -d"
```

```bash
# 2. Solo si la migración fue destructiva (borrar/renombrar columna o tabla)
ssh -i ~/.ssh/id_deploy_academika deploy@157.230.87.2 \
  "cd /opt/academika && docker compose -f compose.prod.yaml run --rm api uv run alembic downgrade <revision_anterior>"
```

Notas:

- **Migraciones aditivas** (agregar columna/tabla) no rompen la versión anterior → el paso 2 no es necesario.
- **Migraciones destructivas** (borrar/renombrar) sí requieren el `downgrade`.
- Para ver el histórico de revisiones: `docker compose -f compose.prod.yaml run --rm api uv run alembic history`.
