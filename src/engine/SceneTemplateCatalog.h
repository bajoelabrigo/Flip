#pragma once

#include "core/Time.h"

#include <QList>
#include <QPair>
#include <QString>
#include <QStringList>

// Scene templates: a whole little edit (photo slots, titles, motion, music) that goes onto the
// timeline as one composition, as in CapCut's templates. Each package is a folder:
//
//   template.json   manifest (below)
//   project.json    the content, as a Flip project document (Project::toJson); asset paths are
//                   relative to the package folder
//   thumbnail.png   card picture; preview.mp4 optional
//   media/…         pictures, music and anything else the project refers to
//
// template.json: {id, displayName, names{<locale>: name}, category, order, width, height,
// durationSec, slots, texts, premium, tags[]}. `slots` and `texts` are counts for the card; the
// slots themselves are the clips in project.json that carry a placeholderId.
struct SceneTemplateEntry
{
    QString id;
    QString displayName; // already in the UI language when the package names it
    QString category;
    int order = 0;
    int width = 1080;
    int height = 1920;
    drift::TimeUs durationUs = 0;
    int slots = 0;
    int texts = 0;
    bool premium = false;
    QStringList tags;
    QString packageDir;
    QString projectPath;
    QString thumbnailPath;
    QString previewPath;
};

const QList<SceneTemplateEntry> &sceneTemplateCatalog();
const SceneTemplateEntry *sceneTemplateForId(const QString &id);

// {id, label} in catalog order, for the category chips.
QList<QPair<QString, QString>> sceneTemplateCategories();
QString sceneTemplateCategoryLabel(const QString &categoryId);

void reloadSceneTemplateCatalog(const QStringList &packageRoots = {});
QStringList defaultSceneTemplateSearchPaths();
