# Sistema de diseño y decisiones de arquitectura de la interfaz

## 1. Principios
1. **Una tarea por pantalla**: vender, ver menú, ver reportes. Lo importante (total, botón principal) siempre visible.
2. **Consistencia**: todo sale de tokens (`static/style.css`) y componentes (`templates/components/ui.html`).
3. **Móvil primero**: el mesero vende desde el celular. Botones de 46 px mínimo, barra de pestañas abajo.
4. **Mejora progresiva**: sin JavaScript los formularios, filtros por enlace y login siguen funcionando; el JS (`static/app.js`) agrega el pedido en vivo, avisos y confirmaciones.

## 2. Tokens (sección 1 de `style.css`)
| Categoría | Tokens |
|---|---|
| Color de marca | `--brand` (rosado), `--accent` (azul), `--sun` (amarillo del Maxi Cono) |
| Superficies y texto | `--bg`, `--surface`, `--surface-2`, `--border`, `--text`, `--text-2` |
| Semánticos | `--ok`/`--ok-bg`, `--bad`/`--bad-bg` |
| Espaciado | `--s1` 4 · `--s2` 8 · `--s3` 12 · `--s4` 16 · `--s5` 24 · `--s6` 32 px |
| Radios y sombras | `--r1` 10 · `--r2` 16 · `--r3` 24 · `--sh1`, `--sh2` |
| Tipografía | Fredoka; `--fs-s`, `--fs-m`, `--fs-l`, `--fs-xl` |
| Interacción | `--tap` 46 px, `--t` .15 s |

**Modo oscuro**: `:root[data-theme=dark]` solo redefine los tokens; ningún componente tiene colores fijos. Para cambiar la marca basta editar la sección de tokens.

## 3. Componentes (`templates/components/ui.html`)
| Macro | Variantes / parámetros | Estados | Accesibilidad |
|---|---|---|---|
| `btn` | primary, ghost, danger · sm, md, lg · enlace o botón | hover, active, focus, disabled | foco visible, alto ≥ 46 px (36 px en `sm` dentro de listas) |
| `card`, `page_header` | título opcional, acciones | — | `h1` único por página |
| `kpi` | icono, tono ok/bad | — | icono decorativo `aria-hidden` |
| `badge` | ok, bad, neutro | — | no depende solo del color: siempre lleva texto |
| `field`, `switch` | ayuda, requerido, atributos | foco, requerido | `label` envolvente |
| `chips`, `segmented` | filtro JS / filtro por enlace | activo | `role=group`, `aria-current` |
| `bars` | valor y porcentaje | vacío | texto con el valor junto a la barra |
| `empty` | icono, texto, acción | — | siempre ofrece el siguiente paso |
| `confirm_form` | mensaje | modal | `<dialog>` nativo, cierra con Esc |

Patrones: **POS** (cuadrícula de productos + resumen fijo + barra de total en móvil), **tablero** (KPIs + tarjetas), **formulario lateral** (lista + formulario sticky), **avisos** (toast de éxito/error).

## 4. Navegación
Definida en `web/navigation.py` (`NAV`). Agregar una sección = una línea. Se filtra por rol (público / staff / admin) y alimenta la barra superior (escritorio) y la barra inferior (móvil) desde la misma lista.

## 5. Decisiones de arquitectura y trade-offs
| Decisión | Por qué | Costo |
|---|---|---|
| Plantillas Jinja + macros en vez de React | Equipo de una persona, aprender Python, páginas rápidas | Menos interactividad que una SPA |
| JS vanilla de ~60 líneas | Sin build ni dependencias | Si crece mucho, pasar a HTMX o Alpine.js |
| Rutas con redirección y aviso (PRG) | Evita reenviar formularios | Los avisos viajan por la URL |
| Lista de navegación única | Evita menús duplicados | — |
| Emojis como iconos | Cero dependencias | Se ven distinto según el dispositivo; luego usar SVG propios |

**Qué revisar cuando crezca**: fotos reales de productos y el logo; paginación en ventas y contabilidad; operación sin internet (PWA); varias sucursales (tabla `locations`); i18n; mover los reportes a consultas SQL; pruebas visuales automáticas.
