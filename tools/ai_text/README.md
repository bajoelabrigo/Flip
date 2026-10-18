# Texto con IA (0.17.0)

Herramientas para el extra `texto.ia` (paraphrase-multilingual-MiniLM-L12-v2, ONNX int8, Apache-2.0).

- `unigram_check.py <carpeta con tokenizer.json>`: compara el tokenizador sencillo que usa la app
  (`engine/TextEmbedder.cpp`: NFKC, separar por espacios, «▁» delante, la mejor segmentación de
  cada palabra) con el de Hugging Face, y escribe `vocab.txt` (una pieza y su puntaje por línea) para
  el extra. Dio 12 de 12 iguales (español, francés, alemán, japonés, emojis).
- `match_check.py <carpeta del modelo> <respuesta de list_text_presets>`: muestra qué estilo elegiría
  la IA para unas ideas de prueba. `hints.json` es la descripción de cada estilo incluido; la misma
  tabla está en `AppController::addAiText` (`kStyleHints`). Con ella: 10 de 10 elecciones sensatas.

Necesita un entorno con `tokenizers`, `onnxruntime` y `numpy`. El modelo se baja de
`https://huggingface.co/Xenova/paraphrase-multilingual-MiniLM-L12-v2` (`onnx/model_quantized.onnx`
y `tokenizer.json`).
