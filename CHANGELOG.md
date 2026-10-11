# Changelog

## [0.4.0](https://github.com/laendoor/academika/compare/v0.3.0...v0.4.0) (2026-10-11)

### Features

* **admin:** tabla de settings genérica + UI backoffice ([#49](https://github.com/laendoor/academika/issues/49)) ([113845a](https://github.com/laendoor/academika/commit/113845a281ee545cdcaf8e05e45a43cdc4d52d79))

### Bug Fixes

* **infra:** rate-limit de /logs/ apto para carga de pagina (10r/s, burst 30) ([27d99c1](https://github.com/laendoor/academika/commit/27d99c133b527df10949e551ebdc029340508a5c))
* **review:** self-review [#49](https://github.com/laendoor/academika/issues/49) — draft persistente, rollback, encode key, validación ([#49](https://github.com/laendoor/academika/issues/49)) ([5b38ec4](https://github.com/laendoor/academika/commit/5b38ec4be20c5130937cf91b957a65cd872eab6b))

## [0.3.0](https://github.com/laendoor/academika/compare/v0.2.8...v0.3.0) (2026-10-11)

### Features

* **api:** admin-only delete user with self-delete and log-events guards ([e9ae3dd](https://github.com/laendoor/academika/commit/e9ae3ddfc54ee5f0456ae74fbb8b142990c4aeca))
* **api:** expose user-roles lookup and protect lookups endpoints ([65c2b2b](https://github.com/laendoor/academika/commit/65c2b2bfb6fc2d9a43201c8701404c9d90e499fd))
* **api:** protect CRUD endpoints with dir+admin auth ([4b4140e](https://github.com/laendoor/academika/commit/4b4140ebf5347cce81ec86f0127385a50247c1e9))
* **infra:** log viewer Dozzle en /logs/ ([#41](https://github.com/laendoor/academika/issues/41)) ([1446f68](https://github.com/laendoor/academika/commit/1446f68835a696ef2a5aadc6d24fbfda6127aafe))
* **web:** add delete user action to admin users panel ([d4724ee](https://github.com/laendoor/academika/commit/d4724eefda81a1069085ef4d0d996e673a623edf))
* **web:** add invite client and BFF proxies for user roles ([8a6d408](https://github.com/laendoor/academika/commit/8a6d408bb24b094807c68b6808e95a2067293fa4))
* **web:** add invite user form to admin users panel ([9807ec9](https://github.com/laendoor/academika/commit/9807ec979576186be5cf6bf65205408023fc2cb1))

### Bug Fixes

* **review:** address PR [#77](https://github.com/laendoor/academika/issues/77) comments ([93b80f7](https://github.com/laendoor/academika/commit/93b80f7663d8ca4748ef72ec8bb5982043284210))

## [0.2.8](https://github.com/laendoor/academika/compare/v0.2.7...v0.2.8) (2026-09-20)

## [0.2.7](https://github.com/laendoor/academika/compare/v0.2.6...v0.2.7) (2026-08-23)
