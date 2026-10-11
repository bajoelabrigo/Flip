#pragma once

#include <QList>
#include <QString>
#include <QStringList>

// File-based sound-effect packages: sound-effects/<pack-id>/{pack.json, *.wav|*.ogg|*.mp3},
// discovered like the sticker and font packages. pack.json:
//
//   {"id", "name", "order", "categories": [{"id", "label"}],
//    "sounds": [{"id", "label", "category", "file", "duration"}]}

struct SoundEffectEntry
{
    QString id; // "<pack-id>/<sound-id>"
    QString label;
    QString category;
    QString path; // absolute
    double duration = 0.0; // seconds
};

struct SoundEffectCategory
{
    QString id;
    QString label;
};

QList<SoundEffectEntry> soundEffects();
QList<SoundEffectCategory> soundEffectCategories();
void reloadSoundEffectCatalog(const QStringList &packageRoots = {});
