#pragma once

#include "TextStyle.h"

#include <QList>
#include <QPair>
#include <QString>

// The two galleries of the text inspector that CapCut users reach for first:
//
//  - Quick styles ("Estilo preestablecido" and the Efectos page): a fill, an outline, a shadow,
//    a glow, a gradient or a 3D extrude, applied over the clip's own font and size.
//  - Bubbles (the Burbuja page): a background shape — speech balloon, burst, tag, ribbon, brush
//    stroke… — with its colours, behind the text.
//
// Both are recipes, not stored presets: applying one rewrites part of the style, and the result is
// an ordinary style the user can keep editing.

namespace drift {

struct TextGalleryEntry
{
    QString id;
    QString label;    // translated
    QString category; // a category id from the matching *Categories() list
};

QList<TextGalleryEntry> textQuickStyles();
QList<QPair<QString, QString>> textQuickStyleCategories(); // id, translated label
// Replaces the layer stack with the recipe's (scaled to the style's pixelSize); font, size, case,
// background and animation stay. False for an unknown id.
bool applyTextQuickStyle(TextStyle &style, const QString &id);

QList<TextGalleryEntry> textBubbles();
QList<QPair<QString, QString>> textBubbleCategories();
// Sets the background (shape, colours, border, padding) and a text colour that reads on it.
// "none" removes the background. False for an unknown id.
bool applyTextBubble(TextStyle &style, const QString &id);

} // namespace drift
