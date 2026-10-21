# Plan de la 0.19.0 — máscaras en textos, textos 100 % editables, seguimiento como CapCut

Rama `flip/v0.19.0` (sale de `main` = 0.18.3), en la copia de trabajo `codigo\Flip-v019` (`git worktree`), para no
mezclarla con `flip/stock-tendencias-texto`, que solo tiene herramientas de Stock.

Pedidos de Jorge (2026-10-21):
1. «Las máscaras en los textos quedó pendiente».
2. «Que todo absolutamente de los textos se pueda editar, de manera que los usuarios puedan usar nuestros textos
   para crear los propios».
3. «El seguimiento de rostro o cámara como el que tiene CapCut y Filmora, no sé si está funcionando».

## 1. Máscaras en textos — HECHO (falta probar en ventana)
- Auditoría: el motor ya dibujaba las máscaras de un texto, pero la interfaz lo bloqueaba (sin `maskable` en
  `inspectorCaps`, `linkedMaskClips` solo para video/imagen, `MasksTab.qml` excluía texto y subtítulos).
- «Texto como forma de máscara» ya existía (`MaskShape::Text`): la nota de pendiente era vieja.
- Arreglos (`131a9`):
  - Texto y subtítulo son `maskable`; la lista y el panel de máscaras los aceptan.
  - `FrameCompositor::masksInLayerFrame`: la máscara se coloca sobre la caja del texto (donde la vista previa dibuja
    las asas), no sobre la imagen con margen (bordes, sombras, animación). Sin esto el corte salía corrido y estirado.
  - Prueba `EditorStateTest::textClipTakesMasks`.
- **Falta:** probar en ventana que las asas coinciden con el corte (texto con borde grueso y animación).
- Web: no tiene máscaras en textos (`inspectorTabs.ts`, `textLayer.ts`, y el `.flip` las pierde). Pendiente.

## 2. Textos 100 % editables — HECHO en el escritorio (falta probar en ventana)
Auditoría campo por campo de los 590 estilos de Stock contra el inspector. Ya se podía casi todo y «Guardar como mi
estilo» guarda el estilo entero. Huecos cerrados (`38dad`):
- **Forma de la caja** (Fondo › Forma): cambia solo la forma; la galería Burbuja sigue reemplazando el look entero.
- **Interruptores de las animaciones** (cursor de la máquina de escribir): se guardan como 0/1 y el botón buscaba
  `true`; siempre salía apagado y no se podía quitar.
- **Curvas**: faltaban «Suave» (`smooth`) y «Acelerar» (`easeIn`), que usan 644 ranuras de Stock.
- **Tinte de los efectos de relleno** (brillo, neón, cromo): `PaintEditor` solo mostraba color para sólido.
- **Desplazamiento X/Y en todas las capas** (no solo sombra): separación RGB, fantasma, estela.
- **Pasos de la extrusión**.
- **Píldora del acento**: relleno y radio; **desfase** del acento («empezar en la palabra»).
- Rangos: ancho de la caja hasta 200 %, tamaño del acento desde 0,2, altura de «lluvia» negativa.
- **Actualizar un estilo propio** con el texto seleccionado (`TextPresetStore::update`, menú de Mis estilos).
- **Animaciones propias**: «Guardar como mi animación» (`saveTextAnimationAsPreset`, categoría «Míos») y menú con
  Renombrar, Exportar y Borrar en las tarjetas `user:` (el C++ existía, nadie lo llamaba).
- Pruebas: `CoreTest::userTextPresetsRoundTrip` (update), `EditorStateTest::textAnimationSavesAsOwnPreset`.
- **Falta:** traducciones (`lupdate` + `drift_es.ts` y los demás idiomas), probar en ventana.
- Menores sin hacer: instalar el mismo estilo de Stock dos veces crea un duplicado; la importación ignora
  `names.en`/`sampleTexts`.
- Web: instala los estilos de Stock simplificados (solo la primera capa de cada tipo, sin efectos ni acento). Pendiente
  decidir: ampliar su modelo o avisar.

## 3. Seguimiento (CapCut / Filmora) — POR HACER
Auditoría: no existe en ninguna de las dos apps. Hay piezas:
- Escaneo de caras por fotograma (`FaceTrackingController`, `FaceTrack`, sidecar en `AppData/facetracks`).
- `auto_reframe` (solo MCP): convierte la cara en fotogramas clave x/y/w/h del propio video.
- Estabilizar (vid.stab) funciona en las dos apps; en la web `stabilize/motion.ts` hace block matching.
- SAM 2 sigue a un sujeto, pero da una máscara, no una posición.

Lo que falta: un seguidor de región, enlazar la posición de un texto/sticker/efecto a esa trayectoria (fotogramas
clave), la interfaz «Seguimiento» y un efecto de difuminar/pixelar cara.

## Estado de la compilación
- Ensayo `build.yml` (Windows) run 39685634394 sobre `38dad`.
