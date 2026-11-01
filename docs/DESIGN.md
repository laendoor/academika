# Diseño — Académika

Referencia de la paleta, la tipografía y las superficies de la app. El origen del
color es `apps/web/src/app/globals.css`: este documento explica los roles y los
contrastes que se midieron para elegirlos, no los reemplaza.

Todos los contrastes son WCAG 2.1 medidos contra blanco (`#FFFFFF`), salvo
donde se aclare.

## Paleta

### Anclas

| Token     | Hex       | Rol                                   | Contraste |
| --------- | --------- | ------------------------------------- | --------- |
| `ink`     | `#020B07` | Texto principal y tinta sobre relleno | 19.93:1   |
| `surface` | `#F2FDFA` | Tinte de bloque; no es el fondo       | —         |
| `brand`   | `#57BC99` | Marca, éxito, relleno de acciones     | 2.32:1    |
| `soft`    | `#A0B8DA` | Relleno secundario, series de datos   | 2.03:1    |
| `accent`  | `#4DADE6` | Enlaces, foco, series de datos        | 2.49:1    |

Ninguno de los tres colores de marca sirve como tinta: sobre el blanco dan 2.32,
2.03 y 2.49:1, muy por debajo de AA. Son rellenos: encima va `ink`, que da 8.60,
9.84 y 8.01:1. Para texto de color se baja un escalón a `brand-700` (5.55:1) o
`accent-700` (5.78:1).

### Rampas

Cada familia va de 50 a 950 con el ancla en el 500. Las rampas se generaron en
OKLCH desde el ancla, con el croma topado en el del 500 para que ningún escalón
se salga del gamut sRGB.

**brand**

| 50        | 100       | 200       | 300       | 400       | 500       | 600       | 700       | 800       | 900       | 950       |
| --------- | --------- | --------- | --------- | --------- | --------- | --------- | --------- | --------- | --------- | --------- |
| `#EDFFF7` | `#D6F6E8` | `#B4E7D2` | `#90D7BB` | `#73CBAA` | `#57BC99` | `#319B79` | `#007759` | `#00634A` | `#004B37` | `#002D20` |

**soft**

| 50        | 100       | 200       | 300       | 400       | 500       | 600       | 700       | 800       | 900       | 950       |
| --------- | --------- | --------- | --------- | --------- | --------- | --------- | --------- | --------- | --------- | --------- |
| `#F7FAFF` | `#E8F0FD` | `#D3E1F5` | `#BFD1EB` | `#AFC5E4` | `#A0B8DA` | `#8097B8` | `#637896` | `#51637D` | `#3F4D61` | `#293240` |

**accent**

| 50        | 100       | 200       | 300       | 400       | 500       | 600       | 700       | 800       | 900       | 950       |
| --------- | --------- | --------- | --------- | --------- | --------- | --------- | --------- | --------- | --------- | --------- |
| `#F5FBFF` | `#DBF0FF` | `#B0DFFF` | `#89CCF8` | `#6BBEF2` | `#4DADE6` | `#258CC3` | `#006C9D` | `#00577F` | `#004060` | `#00263A` |

**sage**

| 50        | 100       | 200       | 300       | 400       | 500       | 600       | 700       | 800       | 900       | 950       |
| --------- | --------- | --------- | --------- | --------- | --------- | --------- | --------- | --------- | --------- | --------- |
| `#EDFAF5` | `#E5F2EC` | `#D1DED9` | `#BBC8C2` | `#9CA8A3` | `#808C87` | `#727C78` | `#5D6763` | `#38433E` | `#212C27` | `#050D0A` |

`sage` es el neutro y sale del hue del texto (168°), no del brand: un gris con un
dejo verde, del mismo lado del círculo cromático que la tinta. No se pisa la
paleta `zinc` de Tailwind: un `text-zinc-600` que apunta a verde es una mentira
semántica para el que lee el código después.

Los escalones de `sage` tienen roles fijos:

| Escalón    | Uso                          | Contraste |
| ---------- | ---------------------------- | --------- |
| `sage-200` | Bordes de cards y tablas     | —         |
| `sage-600` | Íconos y bordes de controles | 4.31:1    |
| `sage-700` | Texto secundario             | 5.86:1    |
| `sage-800` | Texto con peso medio         | 10.29:1    |

`sage-600` no llega a AA para texto: queda para íconos y bordes. Un texto
secundario que se lea va en `sage-700`.

### Semánticos

| Token     | Hex       | Rol                       | Contraste |
| --------- | --------- | ------------------------- | --------- |
| `success` | `#007759` | Operación completada      | 5.55:1    |
| `warning` | `#A16207` | Aviso, dato parcial       | 4.92:1    |
| `danger`  | `#B42318` | Error, acción destructiva | 6.57:1    |

Verde es marca y también éxito: `success` es el `brand-700`, así que no hay dos
verdes compitiendo. Un badge de estado usa el semántico como texto y el mismo
color al 10% como fondo, no la escala de Tailwind.

## Tipografía

**Libre Franklin** en toda la app (`--font-sans`). Es el revival libre de
Franklin Gothic, la tipografía que el manual de la UNQ define para piezas
gráficas.

**JetBrains Mono** para lo técnico (`--font-mono`): log de imports, hash y sha,
valores de configuración y bloques `<pre>`. Se eligió por la altura de x, que
aguanta el peso de Libre Franklin, y por tener `0`/`O` y `1`/`l`/`I`
distinguibles, que es justo lo que se lee ahí.

No hay una escala tipográfica con tokens: los tamaños se escriben con las
utilidades de Tailwind (`text-sm`, `text-xs`, `text-2xl`), como hasta ahora.

## Superficies

- El fondo de la app es blanco puro; el texto, `ink`.
- Las cards son blancas con borde `sage-200`. Sin sombras nuevas: la elevación
  que hay (modales, dropdowns) se queda como está.
- Login y sidebar usan `brand` como acento y `ink` como texto; las tablas y
  badges, `sage` para estructura y los semánticos para estado.
- **Sin dark mode.** La app se ve igual con el sistema en claro o en oscuro. Un
  dark mode real es otro trabajo, con sus propios contrastes.

## Paleta de datos

Seis series para gráficos, en este orden:

| #   | Hex       | Nota                           |
| --- | --------- | ------------------------------ |
| 1   | `#007759` | `brand-700`                    |
| 2   | `#006C9D` | `accent-700`                   |
| 3   | `#A16207` | `warning`                      |
| 4   | `#B42318` | `danger`                       |
| 5   | `#727C78` | `sage-600`                     |
| 6   | `#7F84CC` | periwinkle, sólo para gráficos |

Dos advertencias que no se pueden resolver con color:

- `soft` y `accent` están a ΔE 9.5: son dos azules y no se usan juntas en el
  mismo gráfico. Por eso la serie 2 es `accent-700` y no `accent-500`.
- Bajo deuteranopia, `warning` y `danger` colapsan (ΔE 3.7). Cuando esas dos
  categorías conviven, necesitan etiqueta directa o patrón: nunca sólo color.

## Reglas

- Ningún `--color-*` vive fuera de `@theme`: una variable suelta en `:root` no
  genera utilidades y termina siendo un token muerto.
- Los colores se usan por su rampa (`sage-700`), no por un alias semántico
  nuevo. Migrar todo a `bg-surface` / `text-muted` es otra pasada.
- El logo (ticket #82) hereda esta paleta: no se agrega un color fuera de acá.
