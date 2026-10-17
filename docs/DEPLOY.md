# Deploy y Rollback

## Flujo de deploy

1. `make release` crea un tag `vX.Y.Z` y lo pushea
2. El workflow `.github/workflows/deploy.yml` se dispara con el tag
3. Build + push de imágenes (`leandrojdl/academika-api` + `academika-web`) a Docker Hub
4. Deploy al droplet: `pull` → `migrate` → `seed` → `up`

## Migraciones

`alembic upgrade head` corre en el deploy, **antes** de `up -d`. Si falla, el deploy aborta y la versión anterior sigue corriendo (prod intacto).

## Seeds

- **`seeds.runner reference`** (LKPs de referencia) corre en el deploy, después de las migraciones. Es idempotente y prod-safe.
- **`seeds.create_admin`** (primer usuario admin) es **manual** e interactivo — no va en el CD. Se ejecuta en el servidor:

```bash
cd /opt/academika && docker compose -f compose.prod.yaml exec -it api uv run python -m seeds.create_admin
```

## Log viewer (Dozzle)

`compose.prod.yaml` incluye Dozzle (`amir20/dozzle:v11`), solo vía nginx en
`https://academika.net.ar/logs/` con login propio. En local prende junto al
resto (`http://localhost:8080/logs/`, sin auth).

### Setup one-time en el droplet (manual, como `create_admin`)

Hacerlo ANTES del release: el release levanta Dozzle solo, y sin `users.yml`
Dozzle no arranca (fail-closed), ni la ruta `/logs/` existe sin el location.

Dozzle lee usuarios de `/data/users.yml` (no hay env para passwords):

```bash
mkdir -p /opt/academika/dozzle-data
docker run --rm amir20/dozzle:v11 generate admin --password '<PASSWORD>' \
  --email admin@unq.edu.ar --name Admin --user-roles none > /opt/academika/dozzle-data/users.yml
chmod 600 /opt/academika/dozzle-data/users.yml
```

(`--user-roles none`: solo lectura de logs; sin roles el default es todos.)

Copiar el `location /logs/` de `infra/nginx.conf` al server block, agregar en
el bloque `http` del nginx principal:

```nginx
limit_req_zone $binary_remote_addr zone=logs:10m rate=10r/s;
```

(10r/s con burst 30: la página de login carga ~15 assets juntos; contra un
password fuerte ese rate no le sirve a un brute-force.)

y recargar:

```bash
sudo nginx -t && sudo systemctl reload nginx
```

### Notas

- El `compose.prod.yaml` se sincroniza solo en cada release: el servicio
  levanta sin pasos extra. El `users.yml` vive fuera de git y sobrevive.
- Dozzle corre con actions y shell apagados (defaults) y `roles: none`
  (solo lectura de logs). El socket va en `:ro`.
- Smoke post-release: `/logs/` sin login rechaza; con login muestra api/web.

## Rollback manual

Si un deploy sale mal **después** de aplicar (la migración pasó pero hay un bug):

```bash
# 1. Redeployar la imagen anterior (en el servidor)
cd /opt/academika && IMAGE_TAG=<version_vieja> docker compose -f compose.prod.yaml up -d
```

```bash
# 2. Solo si la migración fue destructiva (borrar/renombrar columna o tabla) (en el servidor)
cd /opt/academika && docker compose -f compose.prod.yaml run --rm api uv run alembic -c apps/api/alembic.ini downgrade <revision_anterior>
```

Notas:

- **Migraciones aditivas** (agregar columna/tabla) no rompen la versión anterior → el paso 2 no es necesario.
- **Migraciones destructivas** (borrar/renombrar) sí requieren el `downgrade`.
- Para ver el histórico de revisiones: `docker compose -f compose.prod.yaml run --rm api uv run alembic -c apps/api/alembic.ini history`.
