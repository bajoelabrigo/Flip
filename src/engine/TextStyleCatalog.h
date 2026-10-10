#pragma once

#include <QStringList>

// File-based text-style packages: text-styles/<pack-id>/pack.json, discovered the same way as font
// and sticker packages. A pack lists categories and styles; each style is a text style object in
// the project format (core/TextStyle textStyleFromJson), so a pack is the user's "Save style…"
// library in bulk:
//
//   {"id", "name", "order", "categories": [{"id", "label"}],
//    "styles": [{"id", "label", "category", "sampleText", "style": {…}}]}
//
// The styles land in core's add-on preset registry under "pack:<pack-id>/<style-id>".
void reloadTextStyleCatalog(const QStringList &packageRoots = {});
