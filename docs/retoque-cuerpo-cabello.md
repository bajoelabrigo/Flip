# Retoque › Cuerpo y Cabello — plan (2026-10-15)

## Modelos (Apache-2.0, verificado en sus model cards)
- **Cuerpo:** MediaPipe Pose Landmarker *full* (BlazePose GHUM): `pose_detector.tflite` (224×224) +
  `pose_landmarks_detector.tflite` (256×256 → 39 puntos × 5, presencia, máscara 256×256). 9,4 MB.
  https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/latest/pose_landmarker_full.task
- **Cabello:** MediaPipe Selfie Multiclass 256×256 (fondo, pelo, piel del cuerpo, piel de la cara, ropa,
  otros). 16,4 MB. https://storage.googleapis.com/mediapipe-models/image_segmenter/selfie_multiclass_256x256/float32/latest/selfie_multiclass_256x256.tflite
- Conversión: `tf2onnx --tflite X.tflite --output X.onnx --opset 17` (entorno `flip-addons/work/pose/.venv`).
- Descartados: BiSeNet/CelebAMask (no comercial), SCHP (pesos sin licencia), YOLO-pose (AGPL), RTMPose (pesos
  con datos de investigación).

## Cómo encaja (calcado del rostro, ver `FaceLandmarker`, `FaceTrackingController`, `FaceTrack`)
- **Cuerpo:** `PoseLandmarker` (ORT con `drift::ort::buildSessions`, `DRIFT_POSE_MODEL_DIR`, tipo de extra
  `pose-model`) → trabajo de escaneo como `FaceTrackingController::detect` (QtConcurrent, progreso, cancelar,
  seguimiento con la pose anterior) → sidecar JSON `AppData/posetracks` → `Clip::poseTrackPath` +
  `poseTrackSrcOffsetUs` → al componer, `sampleAll` interpolado → uniforms `u_pose*` (como
  `applyFaceUniforms`) → efecto `body.reshape` con `"requires": "pose"` (añadirlo en
  `EffectPackageLoader.cpp:70-90`): warp inverso en el fragment shader (cintura, cuerpo, piernas, hombros,
  cabeza, brazos), limitado por la máscara de la persona. Suavizado One-Euro por punto.
- **Cabello:** `HairSegmenter` (ORT, `DRIFT_HAIR_MODEL_DIR`, tipo `hair-model`) → trabajo como
  `SegmentationController` → video de cobertura con `MatteWriter` → `Clip::hairMattePath` +
  `hairMatteSrcOffsetUs` → textura propia como la de profundidad (`PipelineAux`, unidad de textura nueva,
  preludio `"requires": "hair"`) → efecto `hair.color`: cambia tono y saturación conservando la luminancia.
- UI: `VideoInspector.qml` (página Retoque, `areas` rostro/cuerpo/cabello en :347-352; aviso «sin modelo» en
  :504-514): `bodySections`/`hairSections`, botón «Analizar cuerpo»/«Analizar cabello» como «Escanear caras».
- Extras: recetas en `flip-addons/modelos.py` (`cuerpo.pose`, `cabello.segmentacion`), `build.py`, subir al
  release `packages` y luego el `index.json` (en ese orden).
- Pruebas a copiar: `tst_engine` `faceTrackRoundTripsAndInterpolates`, `faceRetouchPassesThroughWithoutFace`,
  `compositorAppliesFaceWarpFromBakedTrack`; `tst_core` `faceTrackSerialization`.

## Validación en Python (2026-10-15, `flip-addons/work/pose/check.py`)
- `pose_detector.tflite` no se convierte (tf2onnx: «cannot reshape array of size 96»). Se trabaja **sin
  detector**: primera pasada del modelo de puntos sobre el cuadro entero (cuadrado, con bordes negros), y
  luego tres pasadas sobre el ROI de MediaPipe: centro = punto auxiliar 33, lado = 2·|p34 − p33|·1,25.
  Con el ROI por la caja de los puntos visibles los hombros caían en la cara; con el de los auxiliares,
  bien en 3 de 4 fotos de prueba (la cuarta, con chaqueta y brazo delante, aceptable).
- Entrada de los dos modelos: RGB **0..1** (con −1..1 el cabello sale mucho peor).
- Salida de puntos: `Identity` 39×5 (x, y en píxeles del recorte de 256, z, visibilidad y presencia en
  logits → sigmoide).
- Cabello: segmentar sobre el **cuadrado de la persona** (ROI de la pose ×1,15), no sobre el cuadro
  aplastado ni sobre un recorte de la cabeza (corta el pelo largo). Clase 1 = pelo. Límite del modelo:
  una gorra sobre el pelo cuenta como pelo.
