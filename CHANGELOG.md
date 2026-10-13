# Changelog

## [0.6.0](https://github.com/laendoor/academika/compare/v0.5.0...v0.6.0) (2026-10-13)

### Features

* **admin:** cards de carreras y planes en dashboard ([540a189](https://github.com/laendoor/academika/commit/540a189b99f6e06422da81192ac16ee8d86eb0f1))
* **admin:** dashboard en grilla 2x2 con orden Carreras/Materias/Planes/Estudiantes ([fabc397](https://github.com/laendoor/academika/commit/fabc3975960307c346e70bbf052f43c533d477e9))
* **admin:** totales de carreras y planes en useAdminStats ([7905680](https://github.com/laendoor/academika/commit/79056800d4cac25862a7b70094d38e6babfd57a9))
* **api:** hash, preview y email en log de imports ([09914f9](https://github.com/laendoor/academika/commit/09914f9df72618076eacb5b137e982e60175707e))
* **carreras:** listado admin con hook, pagina y link en sidebar ([4711b12](https://github.com/laendoor/academika/commit/4711b12de7f10a90bc49ce6ce6a1ff6a2648f3bd))
* **carreras:** proxy BFF con passthrough de query y propagacion de status ([e5e7b5f](https://github.com/laendoor/academika/commit/e5e7b5f7e1c515a3ce8a820065495fe8225fbd28))
* **correlativas:** endpoint GET con filtro por materia + respuesta expandida ([6d30786](https://github.com/laendoor/academika/commit/6d30786d407110d421c63de3f1c812c9f5676b17))
* **correlativas:** pagina admin con filtro por materia + proxy BFF ([2a3fc00](https://github.com/laendoor/academika/commit/2a3fc00cd14c89267879455b96d17adff5403b42))
* **db:** migracion cursadas.creditos ([eace9f3](https://github.com/laendoor/academika/commit/eace9f386c1e2b0bcc7a9954cdc314d0cab96a6b))
* **import:** parsear nucleo y creditos de planes ([f997c47](https://github.com/laendoor/academika/commit/f997c47ef244bcabc8a457adc49a14913783f4b9))
* **import:** persistir nucleo/creditos en Materia y credits en Cursada ([3c70641](https://github.com/laendoor/academika/commit/3c706414e31e410d163ab50d8f8644e4fb428092))
* **lookups:** exponer nivel-carrera y nucleo-carrera ([#67](https://github.com/laendoor/academika/issues/67)) ([0a97d48](https://github.com/laendoor/academika/commit/0a97d48da69f821e8f4967f145edf77e15694216))
* **planes:** detalle con materias y filtro por carrera ([b418bb7](https://github.com/laendoor/academika/commit/b418bb7a6f1b0267739ec33ebdbdb47816c2f939))
* **web:** BFF y hooks de planes con filtro por carrera ([4f85c07](https://github.com/laendoor/academika/commit/4f85c0705285849f0916cc5c18b5e17ab1fd380a))
* **web:** detalle expandible de importaciones ([22995c4](https://github.com/laendoor/academika/commit/22995c4b56c25887d522267b70a3e493faea8a67))
* **web:** historial de imports en formato log ([1382555](https://github.com/laendoor/academika/commit/1382555f2ec2f578e75b78d59203dd52f2dc523b))
* **web:** pagina admin de planes con modal de materias ([9fb6004](https://github.com/laendoor/academika/commit/9fb60044570775f59d004241b27b60221943c851))
* **web:** unifica historial en /admin/importar ([60c8c83](https://github.com/laendoor/academika/commit/60c8c837c0194df92c18d0f0293ce4aa8f801e06))

### Bug Fixes

* **ci:** after_n_builds en codecov.yml notify, fuera del action ([0b56199](https://github.com/laendoor/academika/commit/0b56199839db031511aba8906f520f15d9f296f8))
* **review:** BFF mapea detail a error, valida skip/limit y testea rama 500 ([de2f758](https://github.com/laendoor/academika/commit/de2f7581061e844f29b56afcd274185532349aaf))
* **review:** carrera embebida, race en modal y encoding ([7a93cff](https://github.com/laendoor/academika/commit/7a93cff7d74e6225832d7fce736c368549feea76))
* **review:** helper list/orders, annotations y asserts ⊆ en lookups ([#67](https://github.com/laendoor/academika/issues/67)) ([e655149](https://github.com/laendoor/academika/commit/e6551499cf5fcd7095358a3065987380323195ff))
* **review:** int seguro, no NULL-clobber, test integracion, menores ([ab774bc](https://github.com/laendoor/academika/commit/ab774bc4afa10131ad606534cb1848a050443c21))
* **review:** modal, icono único, grilla, sample 50 y WS en dev ([61ebefd](https://github.com/laendoor/academika/commit/61ebefdb2d0d55efb8782e6dc60a3e1a5d54a473))
* **review:** propagar 4xx en BFF, cota Query, empty con error, sin estado espejo, aria, tipos, asserts whereclause ([c6eae3d](https://github.com/laendoor/academika/commit/c6eae3d0c38b151436a92bf0d51a0463586866ba))
* **review:** restaurar metadata en docstring de migracion ([2127179](https://github.com/laendoor/academika/commit/2127179373f6ebd6093d136a3b767b4ef318e241))
* **review:** session close, millis Safari y drop de truncated ([ee953f7](https://github.com/laendoor/academika/commit/ee953f783da381ec0ad706b20014d1b96953d8ae))
* **review:** WS en ISO, fecha plana, expand directo y muestra de omitidas ([1692ac9](https://github.com/laendoor/academika/commit/1692ac9028a0351f9aeabbf10f8a71895ac5ad06))
* **version:** update academika-api version to 0.5.0 ([ff1ce3e](https://github.com/laendoor/academika/commit/ff1ce3ec717257beaa02fd76fbdf39b6afaf5a52))
* **web:** aviso de recorte también en filas viejas ([39c0952](https://github.com/laendoor/academika/commit/39c0952ff6c785333c4a76ec4d8a2cc79d77d3b4))
* **web:** orden de imports en SourcesList ([0f82db9](https://github.com/laendoor/academika/commit/0f82db9205923971e154a05364db69f74cde6126))
* **web:** tooltip explicativo de estado en el icono ([93b6354](https://github.com/laendoor/academika/commit/93b635480bb6c50ee68eb7418d4166b693217598))

## [0.5.0](https://github.com/laendoor/academika/compare/v0.4.0...v0.5.0) (2026-10-12)

### Features

* **auth:** dominios permitidos configurables vía settings ([#71](https://github.com/laendoor/academika/issues/71)) ([77531dd](https://github.com/laendoor/academika/commit/77531ddfee76fc698fcf1a534572481245619a7d))
* **backoffice:** versión + sha en sidebar vía build-args ([#81](https://github.com/laendoor/academika/issues/81)) ([121d1fe](https://github.com/laendoor/academika/commit/121d1fe5c4402caeb2218bbeb96d613097a5b80e))

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
