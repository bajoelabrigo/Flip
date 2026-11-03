# Texto a voz como las apps grandes (0.30)

Pedido de Jorge (2026-11-03): «convertir texto en audio, muy usado en videos de YouTube: haz el mismo chequeo que con los
subtítulos y dime qué agregar, corregir y quitar para competir con las apps grandes». Aprobada la lista de abajo
(«sí, anótalo y empieza»); el punto 13 (voces en la nube dentro de la app) queda para que Jorge lo decida.

Cómo seguir: marcar cada punto con su commit; probar en ventana antes de publicar.

## Lo que había (revisión del 2026-11-03)
- Motor en el equipo: Chatterbox Multilingual (extra `voz.chatterbox`, «Voz con IA», pide el motor de IA), 21 idiomas,
  sin cuenta. `engine/ChatterboxTts`, `models/TtsController`, `models/VoiceLibrary`, `qml/components/assets/SpeechTab.qml`,
  `VoiceoverDialog.qml` (voz en off desde un clip de subtítulos).
- Una sola voz incluida («Default»); el resto, clonadas (clip, micrófono o archivo, 3–20 s).
- ElevenLabs y Fish Audio solo para agentes (MCP `tts_generate`), con la clave del usuario.

## Corregir
- [x] 1. `VoiceLibrary::modelVersion()` busca el extra `tts.chatterbox-multilingual`; el publicado es `voz.chatterbox`.
- [x] 2. Textos sin `tr`: «Speaking line %1 of %2…» (`TtsController.cpp`), progreso de clonar y errores del motor
      (`VoiceLibrary.cpp`, `ChatterboxTts.cpp`).
- [x] 3. El idioma de la voz arranca en inglés: que siga el idioma de la interfaz.
- [x] 4. Grabar: el aviso dice 5–20 s y deja guardar desde 3 s; pasado 20 s corta sin avisar. Parar sola a los 20 s.
- [x] 5. Clonar sin progreso ni Cancelar.
- [x] 6. La pestaña Voz pierde el guion y el resultado al cambiar de pestaña.
- [x] 7. Quitar el aviso rojo de «más de 30 s» (el motor ya parte en frases).
- [x] 8. Voz en off desde subtítulos: sin enlace para instalar el modelo, se cierra sola si falla la carga, una línea
      que falla se salta sin avisar.
- [x] 9. Fish Audio en Ajustes «para voz en off» sin que ningún panel lo use (ahora dice «Voz en off a través de agentes de IA»; se queda para el agente).
- [x] 10. «Mi cuenta › Voces» abre la pestaña de texto a voz, pero sus favoritos son del cambiador de voz.
- [x] 11. «Expresividad» con el título repetido.

## Agregar
- [ ] 1. Muchas voces listas (nombre, tipo, muestra): Kokoro (Apache 2.0, ~50 voces, rápido; el editor web ya lo usa)
      para narraciones largas, Chatterbox para clonar y voces con emoción.
- [ ] 2. Velocidad y tono (0,5×–2×), después de generar, para cualquier motor.
- [ ] 3. Escuchar antes de insertar y regenerar.
- [ ] 4. Editar el guion y regenerar (el texto ya se guarda en el medio: `MediaAsset` línea 116).
- [ ] 5. Subtítulos automáticos del audio generado, palabra por palabra (el texto ya se sabe).
- [ ] 6. Guiones largos: progreso por frase, lista de frases para escuchar y rehacer una sola.
- [ ] 7. Importar un guion (.txt/.docx) y pausas `[pausa 1s]`.
- [ ] 8. Diálogo con varias voces (`Ana: …` / `Luis: …`).
- [ ] 9. Leer en voz alta un clip de texto (como CapCut), el audio pegado al texto.
- [ ] 10. Bajar la música debajo de la voz (botón; `duck_under` ya existe para agentes).
- [ ] 11. Doblar: traducir los subtítulos y leerlos con la misma voz.
- [ ] 12. Exportar la voz (WAV/MP3).
- [ ] 13. (Jorge decide) Voces en la nube dentro de la app por nuestro servidor, con cuenta (premium más adelante).

## Quitar
- El aviso rojo de 30 s (Corregir 7).
- ~~Fish Audio de Ajustes~~: se dejó, con el texto corregido (la clave la usan los agentes) (Corregir 9).

## Estado
- 2026-11-03: Corregir 1–11 hechos (rama `flip/subtitulos`, sin compilar): id del extra `voz.chatterbox` (y el viejo),
  textos con `tr`/`translate`, idioma de la voz = el de la interfaz, grabación que se para sola a los 20 s, progreso y
  Cancelar al clonar (`VoiceLibrary::encodeProgress/encodeStatus/cancelEncoding`), guion y resultado guardados en
  `TtsController` (`draftScript`, `lastResultText`), sin el aviso de 30 s, un solo «Expresividad», voz en off desde
  subtítulos con instalar el modelo, error que se queda en la ventana y líneas perdidas avisadas.
