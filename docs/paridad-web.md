# Paridad del editor web con la app de escritorio

Pedido de Jorge (2026-10-18): que el editor web (`flipstudio-app`, getflipstudio.com/editor) quede **igual o lo más
parecido posible** a la app de escritorio. **Empezamos a armarlo mañana, 2026-10-19**, después de publicar la
0.18.1. Este documento es la lista de trabajo: una fila por función, y se actualiza en cada versión.

## Reglas
- **Copiar, no inventar:** nombres, iconos (lucide, los mismos ids que `src/qml/Theme.qml`), colores, orden de
  pestañas y atajos salen del escritorio. Si CapCut o Filmora ya resolvieron cómo se comporta algo, se copia.
- **Nada de código de Drift en la web:** los shaders y el código de Drift son GPL y `flipstudio-app` es privado. Los
  efectos y transiciones de la web se escriben desde cero. Lo que escribimos nosotros (por ejemplo `face_blemish`,
  las plantillas, los generadores de Stock) es nuestro y sí se puede reusar.
- **Un solo formato, el `.flip`:** el escritorio guarda como `.flip` y sigue abriendo los `.drift` de antes (es el
  mismo paquete, solo cambia la extensión: `EditorHeader.qml`, «Flip Studio project (*.flip *.drift)»). La web hoy
  solo conoce `.drift` (`Home.tsx`: `accept=".drift"`, «Importar .drift»; `App.tsx` descarga `.drift`): tiene que
  abrir `.flip` y `.drift` y guardar `.flip`, igual que el escritorio. Todo lo nuevo tiene que sobrevivir el viaje
  escritorio → web → escritorio (`project/driftBundle.ts`).
- **Mismo servidor:** la cuenta de Google y Stock usan `api.getflipstudio.com`, igual que el escritorio.
- Cada versión nueva del escritorio dice en su `docs/plan-<versión>.md` qué parte pasa a la web.

## Estado (revisado en el código el 2026-10-18; ❓ = comprobar mañana en el navegador)

Leyenda: ✅ igual · 🟡 parcial · ⬜ falta · ❓ por comprobar

### Aspecto y navegación
| Función | Escritorio | Web | Notas |
|---|---|---|---|
| Tema oscuro turquesa como Filmora (paneles `#181c1f`, menús `#202427`, acento `#55e5c5`) | 0.17 | ⬜ | `layout/theme.ts` sigue con el tema anterior |
| Pantalla de inicio como Filmora | 0.17 | 🟡 | Hay `Home.tsx`, con otro diseño |
| Cerrar el editor vuelve al inicio | 0.17 | ❓ | |
| Menú arriba (Archivo, Editar, Herramientas, Ver, Avanzado, Ayuda) con atajos | 0.16 | ⬜ | `AppMenuBar.qml` es el modelo |
| Fila de categorías sobre el panel de recursos | 0.16 | 🟡 | Hay `CategoryScrollOn.tsx`; falta la fila completa de `AssetsPanel.qml` |
| Panel izquierdo con barra de iconos e inspector derecho con su barra | 0.9.x | ✅ | |
| Idiomas de la app (13) | sí | ❓ | Comprobar qué idiomas tiene la web |
| Proyectos `.flip` (abrir `.flip` y `.drift`, guardar `.flip`) | sí | ⬜ | La web solo importa y descarga `.drift` |

### Cuenta y Stock
| Función | Escritorio | Web | Notas |
|---|---|---|---|
| Iniciar sesión con Google | 0.10 | ⬜ | En la web es más fácil: el mismo dominio, flujo normal de OAuth |
| Stock (plantillas, música, sonidos, LUT, looks, estilos y animaciones de texto, transiciones, formas, stickers, superposiciones, fondos, contadores, kits) | 0.12–0.18 | ⬜ | Más de 4.000 elementos ya servidos en `api.getflipstudio.com` |
| Inicio de Stock tipo tienda, búsqueda, favoritos y «Pide una plantilla» | 0.14 | ⬜ | |
| Biblioteca de la cuenta («Mis descargas») | 0.12 | ⬜ | |
| Pexels y Pixabay | 0.10 | ⬜ | Ya están detrás del servidor |

### Plantillas
| Función | Escritorio | Web | Notas |
|---|---|---|---|
| Plantillas de escena con huecos «Tu foto aquí» | 0.12 | ⬜ | Leer el mismo paquete (`FORMAT.md` en `tools/scene_templates`) |
| Plantillas de efectos (Intensidad, Caída, Ritmo) | 0.11 | ❓ | Hay rastro de plantillas en 9 archivos; revisar qué cubre |
| Guardar como plantilla / Mis plantillas | 0.13 | ⬜ | |

### Edición en la línea de tiempo
| Función | Escritorio | Web | Notas |
|---|---|---|---|
| Pistas libres, ojo, silencio y candado por pista | 0.9.7 | ✅ | |
| Cortar, duplicar, invertir, marcadores | sí | ✅ | |
| Congelar fotograma como CapCut | 0.17 | 🟡 | Hay `freezeFrame`; comprobar que corte y empuje como en el escritorio |
| Mover con cerrar huecos y borrar con cerrar huecos | 0.16–0.17 | 🟡 | Hay código de cerrar huecos; comprobar los dos casos |
| Arrastre «tipo tetris» | 0.18 | ❓ | |
| Seleccionar varias pistas, agrupar y desagrupar | 0.9.9 / 0.12 | 🟡 | Hay composiciones; falta la selección de pistas |
| Capas de ajuste con «Aplicar a» | 0.9.9 | 🟡 | Hay `AdjustmentLayerSection.tsx` |
| Curvas de velocidad | sí | ⬜ | Solo se conservan al abrir un `.drift` |
| Estabilizar | sí | ⬜ | Solo se conserva al abrir un `.drift` |

### Efectos, transiciones, color
| Función | Escritorio | Web | Notas |
|---|---|---|---|
| Efectos | 78 | 🟡 ~25 | Escribirlos desde cero, por categoría, con las mismas tarjetas |
| Transiciones | 40 | 🟡 10 | Ídem |
| Antes y después al pasar el mouse | 0.17–0.18 | ⬜ | |
| Filtros (LUT) y Efectos de color | 0.16 | 🟡 | Hay `LutPage.tsx` y `cubeLut.ts`; faltan las 200 LUT de Stock |
| Máscaras | sí | 🟡 | Hay `MaskPage.tsx`; falta texto como máscara (tampoco está en el escritorio) |
| Modos de fusión | sí | ✅ | |

### Texto
| Función | Escritorio | Web | Notas |
|---|---|---|---|
| Básico, Burbuja, Efectos y Animación como CapCut | 0.9.6 | ✅ | |
| Contadores animados | 0.17–0.18 | ⬜ | `counterTextAt` y `counterSeconds` en el escritorio |
| Texto con IA (describir la idea) | 0.17 | ⬜ | MiniLM puede correr en el navegador |

### Audio
| Función | Escritorio | Web | Notas |
|---|---|---|---|
| Música y efectos de sonido incluidos | sí | ✅ | `/musica/` en el VPS |
| Mezclador y efectos de audio | sí | 🟡 | Hay `AudioMixer.tsx`; comparar con la pestaña de audio |
| Golpes de música, cortes al ritmo | sí | ⬜ | |
| Silencios, sonoridad, normalizar | sí | ❓ | |

### IA
| Función | Escritorio | Web | Notas |
|---|---|---|---|
| Subtítulos con Whisper | sí | ✅ | Whisper base en el navegador |
| Voz con IA | sí (extra `tts-model`, local) | ✅ | La web usa Kokoro en el navegador; comprobar que las voces e idiomas coincidan |
| Quitar fondo | sí (IA) | 🟡 | La web usa croma (color), no IA |
| Transición con IA y cámara lenta suave (RIFE) | 0.17–0.18 | ⬜ | ONNX Runtime Web con WebGPU, como Whisper |
| Retoque, quitar imperfecciones, cuerpo y cabello | 0.13–0.17 | ⬜ | Necesita caras en el navegador (MediaPipe web) |
| Profundidad, quitar ruido | sí | ⬜ | Al final, o nunca: muy pesados para el navegador |

### Exportar
| Función | Escritorio | Web | Notas |
|---|---|---|---|
| Hasta 4K | sí | ✅ | La web llega a 4K60 |
| 8K, H.265/AV1 | 0.12 | ❓ | Depende de WebCodecs del navegador |
| GIF | sí | ❓ | |

## Orden propuesto (a confirmar con Jorge mañana)
1. **Que se vea igual:** tema turquesa, inicio, menú arriba con atajos y fila de categorías completa; y proyectos
   `.flip` (abrir `.flip`/`.drift`, guardar `.flip`).
2. **Cuenta y Stock:** Google + todo Stock desde `api.getflipstudio.com`.
3. **Plantillas de escena** con el mismo paquete que el escritorio.
4. **Completar efectos y transiciones** escritos desde cero, con antes y después.
5. **Comportamiento de CapCut** que falte: congelar, cerrar huecos, tetris, selección de pistas, curvas de velocidad.
6. **IA en el navegador:** RIFE, texto con IA y caras/retoque. Profundidad y quitar ruido al final.

## Primer paso de mañana
Antes de la web: la próxima versión lleva el arreglo del botón «Actualizar a …» (rama `flip/v0.18.2`, commit
`28ed5`; ver `docs/plan-0.18.1.md`). Se trabaja en esa misma rama.

Abrir el escritorio y la web lado a lado y resolver los ❓ de la tabla. Después, empezar la etapa 1 en una rama de
`flipstudio-app` y desplegar con su `deploy/deploy.sh` al terminar cada etapa.
