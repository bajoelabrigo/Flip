import re
p = r"C:\Users\bajoe\Downloads\Flip\i18n\drift_es.ts"
t = open(p, encoding="utf-8").read()
# "Remove background" is the Video page's name, and the rest of the app calls the feature
# "Eliminar fondo" (MasksTab, the effects). Two names for one thing read as two features.
old = "<source>Remove background</source>\n        <translation>Quitar fondo</translation>"
new = "<source>Remove background</source>\n        <translation>Eliminar fondo</translation>"
n = t.count(old)
t = t.replace(old, new)
open(p, "w", encoding="utf-8").write(t)
print(f"cambiadas {n} entradas de 'Quitar fondo' a 'Eliminar fondo'")
