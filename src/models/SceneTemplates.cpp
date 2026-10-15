// Scene templates (CapCut-style): insert a packaged little edit as one composition, list its
// slots and texts, and fill them. See engine/SceneTemplateCatalog.h for the package format.

#include "AppController.h"

#include "AssetLibrary.h"
#include "MediaBinController.h"
#include "core/SceneTemplateLayout.h"
#include "engine/SceneTemplateCatalog.h"

#include <QCryptographicHash>
#include <QDir>
#include <QFile>
#include <QFileInfo>
#include <QImage>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <QLinearGradient>
#include <QPainter>
#include <QPainterPath>
#include <QStandardPaths>
#include <QUrl>
#include <QUuid>

#include <algorithm>
#include <memory>

namespace {

const QLatin1String kSceneTemplateKind("scene-template");

QJsonObject sceneGenerator(const drift::MediaAsset &asset)
{
    if (asset.kind != drift::MediaKind::Composite
        || asset.generator.value(QStringLiteral("kind")).toString() != kSceneTemplateKind) {
        return {};
    }
    return asset.generator;
}

drift::Clip *findClipAnywhere(drift::Project &project, const QString &clipId)
{
    drift::Clip *found = nullptr;
    project.forEachTrackList([&](QList<drift::Track> &tracks) {
        for (drift::Track &track : tracks) {
            for (drift::Clip &clip : track.clips) {
                if (!found && clip.id == clipId)
                    found = &clip;
            }
        }
    });
    return found;
}

// The slot's box at its first frame: what a filling picture is cut to match.
QSizeF slotSize(const drift::Clip &clip, int canvasW, int canvasH)
{
    const double w = clip.transformW.isEmpty() ? canvasW : clip.transformW.evaluateAt(0);
    const double h = clip.transformH.isEmpty() ? canvasH : clip.transformH.evaluateAt(0);
    return QSizeF(qMax(1.0, w), qMax(1.0, h));
}

// The stand-in a slot shows until it is filled: dark card, a picture glyph, its number and
// "Your photo here". Cached by size and text, so re-inserting a template draws nothing.
QString slotPicture(const QSizeF &slot, int number, const QString &caption)
{
    const double fit = qMin(1.0, 720.0 / qMax(slot.width(), slot.height()));
    const QSize size(qMax(16, qRound(slot.width() * fit)), qMax(16, qRound(slot.height() * fit)));
    const QString key = QStringLiteral("%1x%2-%3-%4").arg(size.width()).arg(size.height()).arg(number).arg(caption);
    const QString dir = QDir(QStandardPaths::writableLocation(QStandardPaths::AppDataLocation))
                            .filePath(QStringLiteral("cache/template-slots"));
    QDir().mkpath(dir);
    const QString path = QDir(dir).filePath(
        QString::fromLatin1(QCryptographicHash::hash(key.toUtf8(), QCryptographicHash::Sha1).toHex().left(16))
        + QStringLiteral(".png"));
    if (QFileInfo::exists(path))
        return path;

    QImage image(size, QImage::Format_ARGB32_Premultiplied);
    QPainter p(&image);
    p.setRenderHint(QPainter::Antialiasing);
    QLinearGradient bg(0, 0, size.width(), size.height());
    bg.setColorAt(0, QColor(0x2b, 0x2f, 0x3d));
    bg.setColorAt(1, QColor(0x17, 0x19, 0x22));
    p.fillRect(image.rect(), bg);

    const double unit = qMin(size.width(), size.height());
    const double margin = unit * 0.06;
    QPen dash(QColor(255, 255, 255, 90), qMax(2.0, unit * 0.008), Qt::DashLine);
    p.setPen(dash);
    p.setBrush(Qt::NoBrush);
    p.drawRoundedRect(QRectF(margin, margin, size.width() - 2 * margin, size.height() - 2 * margin),
                      unit * 0.04, unit * 0.04);

    // Picture glyph: a frame with a sun and two hills.
    const double g = unit * 0.26;
    const QRectF glyph(size.width() / 2.0 - g / 2.0, size.height() / 2.0 - g * 0.85, g, g * 0.78);
    p.setPen(QPen(QColor(255, 255, 255, 200), qMax(2.0, unit * 0.012)));
    p.drawRoundedRect(glyph, g * 0.1, g * 0.1);
    p.setBrush(QColor(255, 255, 255, 200));
    p.drawEllipse(QPointF(glyph.left() + g * 0.3, glyph.top() + g * 0.27), g * 0.08, g * 0.08);
    QPainterPath hills;
    hills.moveTo(glyph.left() + g * 0.08, glyph.bottom() - g * 0.08);
    hills.lineTo(glyph.left() + g * 0.4, glyph.top() + g * 0.42);
    hills.lineTo(glyph.left() + g * 0.58, glyph.top() + g * 0.58);
    hills.lineTo(glyph.left() + g * 0.72, glyph.top() + g * 0.46);
    hills.lineTo(glyph.right() - g * 0.08, glyph.bottom() - g * 0.08);
    hills.closeSubpath();
    p.setPen(Qt::NoPen);
    p.drawPath(hills);

    QFont font;
    font.setBold(true);
    font.setPixelSize(qMax(10, qRound(unit * 0.11)));
    p.setFont(font);
    p.setPen(QColor(255, 255, 255, 235));
    p.drawText(QRectF(0, glyph.bottom() + unit * 0.03, size.width(), unit * 0.14), Qt::AlignCenter,
               QString::number(number));
    font.setBold(false);
    font.setPixelSize(qMax(9, qRound(unit * 0.06)));
    p.setFont(font);
    p.setPen(QColor(255, 255, 255, 170));
    p.drawText(QRectF(margin, glyph.bottom() + unit * 0.17, size.width() - 2 * margin, unit * 0.2),
               Qt::AlignHCenter | Qt::AlignTop | Qt::TextWordWrap, caption);
    p.end();
    image.save(path);
    return path;
}

} // namespace

QVariantList AppController::sceneTemplates() const
{
    QVariantList out;
    for (const SceneTemplateEntry &entry : sceneTemplateCatalog()) {
        out.append(QVariantMap{
            {QStringLiteral("id"), entry.id},
            {QStringLiteral("name"), entry.displayName},
            {QStringLiteral("category"), entry.category},
            {QStringLiteral("categoryLabel"), sceneTemplateCategoryLabel(entry.category)},
            {QStringLiteral("thumbnail"),
             entry.thumbnailPath.isEmpty() ? QString() : QUrl::fromLocalFile(entry.thumbnailPath).toString()},
            {QStringLiteral("preview"),
             entry.previewPath.isEmpty() ? QString() : QUrl::fromLocalFile(entry.previewPath).toString()},
            {QStringLiteral("slots"), entry.slotCount},
            {QStringLiteral("texts"), entry.textCount},
            {QStringLiteral("durationSec"), drift::usToSeconds(entry.durationUs)},
            {QStringLiteral("width"), entry.width},
            {QStringLiteral("height"), entry.height},
            {QStringLiteral("premium"), entry.premium},
            {QStringLiteral("tags"), entry.tags},
        });
    }
    return out;
}

QVariantList AppController::sceneTemplateCategoryList() const
{
    QVariantList out;
    for (const auto &category : sceneTemplateCategories())
        out.append(QVariantMap{{QStringLiteral("id"), category.first}, {QStringLiteral("label"), category.second}});
    return out;
}

QString AppController::insertSceneTemplate(const QString &templateId)
{
    const SceneTemplateEntry *entry = sceneTemplateForId(templateId);
    if (!entry) {
        setLastMessage(tr("That template is not installed"), QStringLiteral("warning"));
        return {};
    }
    if (!m_project.activeSequenceId().isEmpty()) {
        setLastMessage(tr("Templates go on the main timeline: close the composition first"),
                       QStringLiteral("warning"));
        return {};
    }
    QFile file(entry->projectPath);
    if (!file.open(QIODevice::ReadOnly)) {
        setLastMessage(tr("Could not read the template"), QStringLiteral("error"));
        return {};
    }
    QString error;
    drift::Project content = drift::Project::fromJson(QJsonDocument::fromJson(file.readAll()).object(), &error);
    if (!error.isEmpty() || content.tracks().isEmpty()) {
        qWarning("insertSceneTemplate: %s: %s", qPrintable(templateId), qPrintable(error));
        setLastMessage(tr("Could not read the template"), QStringLiteral("error"));
        return {};
    }

    setPlaying(false);
    const drift::Project before = m_project.detachedCopy();

    // An empty project takes the template's shape; anything else keeps its own and the template
    // is fitted into it.
    bool timelineEmpty = true;
    for (const drift::Track &track : m_project.tracks())
        timelineEmpty = timelineEmpty && track.clips.isEmpty();
    if (timelineEmpty && (m_project.width() != content.width() || m_project.height() != content.height()))
        m_project.setResolution(content.width(), content.height());

    QList<drift::Track> tracks = content.tracks();
    drift::scaleTemplateLayout(tracks, content.width(), content.height(), m_project.width(), m_project.height());

    // Its media goes in a bin folder of its own, so the slot pictures and the music do not crowd
    // the user's.
    drift::BinFolder folder;
    folder.id = QUuid::createUuid().toString(QUuid::WithoutBraces);
    folder.name = tr("Template: %1").arg(entry->displayName);
    folder.parentId = m_bin ? m_bin->currentFolderId() : QString();
    m_project.addBinFolder(folder);

    // New ids for everything, so the same template can go in twice.
    QHash<QString, QString> assetIds;
    for (const drift::MediaAsset &source : content.assets()) {
        drift::MediaAsset asset = source;
        if (asset.kind == drift::MediaKind::Composite)
            continue; // one level of nesting: a template holds no compositions of its own
        asset.id = QUuid::createUuid().toString(QUuid::WithoutBraces);
        if (!asset.path.isEmpty() && QDir::isRelativePath(asset.path))
            asset.path = QDir(entry->packageDir).absoluteFilePath(asset.path);
        asset.folderId = folder.id;
        assetIds.insert(source.id, m_project.addAsset(asset));
    }

    bool hasMusic = false;
    for (const drift::Track &track : tracks)
        hasMusic = hasMusic || (track.type == drift::TrackType::Audio && !track.clips.isEmpty());

    const drift::TimeUs startUs = m_playheadUs;
    QSet<QString> ids;
    int slotNumber = 0;
    QHash<QString, QString> standIns; // placeholderId -> its stand-in picture
    for (drift::Track &track : tracks) {
        track.id = QUuid::createUuid().toString(QUuid::WithoutBraces);
        track.locked = false;
        QHash<QString, QString> clipIds;
        for (drift::Clip &clip : track.clips) {
            const QString newId = QUuid::createUuid().toString(QUuid::WithoutBraces);
            clipIds.insert(clip.id, newId);
            clip.id = newId;
            clip.timelineStart += startUs;
            if (assetIds.contains(clip.assetId)) {
                clip.assetId = assetIds.value(clip.assetId);
                if (const drift::MediaAsset *asset = m_project.asset(clip.assetId)) {
                    clip.path = asset->path;
                    clip.thumbnailPath = asset->thumbnailPath;
                    clip.filmstripPath = asset->filmstripPath;
                }
            }
            if (!clip.placeholderId.isEmpty() && clip.type != drift::ClipType::Text
                && clip.type != drift::ClipType::Subtitle && standIns.contains(clip.placeholderId)) {
                // A repeat of a slot: the same stand-in.
                const drift::MediaAsset *picture = m_project.asset(standIns.value(clip.placeholderId));
                clip.assetId = picture->id;
                clip.type = drift::ClipType::Image;
                clip.path = picture->path;
                clip.thumbnailPath = picture->path;
                clip.sourceFrame = QRectF(0, 0, 1, 1);
                clip.srcIn = 0;
                clip.srcOut = clip.timelineDuration;
                clip.placeholderEmpty = true;
            } else if (!clip.placeholderId.isEmpty() && clip.type != drift::ClipType::Text
                && clip.type != drift::ClipType::Subtitle) {
                ++slotNumber;
                const QSizeF box = slotSize(clip, m_project.width(), m_project.height());
                drift::MediaAsset picture;
                picture.kind = drift::MediaKind::Image;
                picture.name = clip.placeholderLabel.isEmpty() ? tr("Slot %1").arg(slotNumber) : clip.placeholderLabel;
                picture.path = slotPicture(box, slotNumber, tr("Your photo or video here"));
                const QImage probe(picture.path);
                picture.width = probe.width();
                picture.height = probe.height();
                picture.folderId = folder.id;
                clip.assetId = m_project.addAsset(picture);
                standIns.insert(clip.placeholderId, clip.assetId);
                clip.type = drift::ClipType::Image;
                clip.path = picture.path;
                clip.thumbnailPath = picture.path;
                clip.sourceFrame = QRectF(0, 0, 1, 1);
                clip.srcIn = 0;
                clip.srcOut = clip.timelineDuration;
                clip.placeholderEmpty = true;
                if (clip.placeholderLabel.isEmpty())
                    clip.placeholderLabel = tr("Photo %1").arg(slotNumber);
            }
            if (hasMusic && clip.type == drift::ClipType::Video)
                clip.suppressEmbeddedAudio = true;
            ids.insert(clip.id);
        }
        for (drift::Transition &transition : track.transitions) {
            transition.fromClipId = clipIds.value(transition.fromClipId, transition.fromClipId);
            transition.toClipId = clipIds.value(transition.toClipId, transition.toClipId);
        }
        for (drift::Clip &clip : track.clips) {
            if (!clip.linkedClipId.isEmpty())
                clip.linkedClipId = clipIds.value(clip.linkedClipId, clip.linkedClipId);
        }
    }
    // Lanes point at their parent by track id; keep that pairing under the new ids.
    {
        QHash<QString, QString> trackIds;
        const QList<drift::Track> &old = content.tracks();
        for (int i = 0; i < tracks.size() && i < old.size(); ++i)
            trackIds.insert(old.at(i).id, tracks.at(i).id);
        for (drift::Track &track : tracks) {
            if (!track.parentTrackId.isEmpty())
                track.parentTrackId = trackIds.value(track.parentTrackId);
            if (!track.spanEndTrackId.isEmpty())
                track.spanEndTrackId = trackIds.value(track.spanEndTrackId);
        }
    }
    if (ids.isEmpty()) {
        m_project = before;
        setLastMessage(tr("This template is empty"), QStringLiteral("warning"));
        return {};
    }

    // On top of the stack, then folded into one composition in their place.
    for (int i = tracks.size() - 1; i >= 0; --i)
        m_project.tracks().prepend(tracks.at(i));
    const QString compositeId = buildCompositeFromClipIds(ids, entry->displayName, {});
    if (compositeId.isEmpty()) {
        m_project = before;
        setLastMessage(tr("Could not place the template"), QStringLiteral("error"));
        return {};
    }
    drift::Clip *composite = findClipAnywhere(m_project, compositeId);
    if (composite) {
        if (drift::MediaAsset *asset = m_project.asset(composite->assetId)) {
            asset->generator = QJsonObject{
                {QStringLiteral("kind"), kSceneTemplateKind},
                {QStringLiteral("templateId"), entry->id},
                {QStringLiteral("templateName"), entry->displayName},
            };
        }
    }
    if (m_assetLibrary)
        m_assetLibrary->syncToProject();
    pushProjectEdit(before, tr("Add template"));
    finishEdit(QString());
    setLastMessage(slotNumber > 0 ? tr("Template added: fill its %n slot(s) in the panel on the right", "", slotNumber)
                                  : tr("Template added"),
                   QStringLiteral("info"));
    selectClipById(compositeId);
    emit sequenceTabsChanged();
    return compositeId;
}

QString AppController::sceneTemplateAssetAt(int trackIndex, int clipIndex) const
{
    // Inside the composition: the template is the one being edited.
    const QString active = m_project.activeSequenceId();
    if (!active.isEmpty()) {
        for (const drift::MediaAsset &asset : m_project.assets()) {
            if (asset.sequenceId == active && !sceneGenerator(asset).isEmpty())
                return asset.id;
        }
        return {};
    }
    if (!isValidClipIndex(trackIndex, clipIndex))
        return {};
    const drift::Clip &clip = m_project.tracks().at(trackIndex).clips.at(clipIndex);
    const drift::MediaAsset *asset = m_project.asset(clip.assetId);
    return asset && !sceneGenerator(*asset).isEmpty() ? asset->id : QString();
}

QVariantMap AppController::sceneTemplateInfo(const QString &compositeAssetId) const
{
    const drift::MediaAsset *asset = m_project.asset(compositeAssetId);
    if (!asset || sceneGenerator(*asset).isEmpty())
        return {};

    struct Slot
    {
        drift::TimeUs start;
        int track;
        QVariantMap map;
    };
    QList<Slot> media;
    QList<Slot> texts;
    const QList<drift::Track> &tracks = m_project.sequenceTracks(asset->sequenceId);
    QSet<QString> seenSlots;
    // Top of the stack is index 0; reading bottom-up numbers slots the way they were laid out.
    for (int t = 0; t < tracks.size(); ++t) {
        for (const drift::Clip &clip : tracks.at(t).clips) {
            if (clip.placeholderId.isEmpty())
                continue;
            const bool isText = clip.type == drift::ClipType::Text || clip.type == drift::ClipType::Subtitle;
            QVariantMap map{
                {QStringLiteral("clipId"), clip.id},
                {QStringLiteral("slotId"), clip.placeholderId},
                {QStringLiteral("label"), clip.placeholderLabel},
                {QStringLiteral("startSec"), drift::usToSeconds(clip.timelineStart)},
                {QStringLiteral("durationSec"), drift::usToSeconds(clip.timelineDuration)},
            };
            if (isText) {
                map.insert(QStringLiteral("text"), clip.textContent);
                texts.append({clip.timelineStart, t, map});
            } else if (seenSlots.contains(clip.placeholderId)) {
                continue; // a repeat of a slot already listed: one fill fills them all
            } else {
                seenSlots.insert(clip.placeholderId);
                const drift::MediaAsset *media_ = m_project.asset(clip.assetId);
                map.insert(QStringLiteral("empty"), clip.placeholderEmpty);
                map.insert(QStringLiteral("kind"), clip.type == drift::ClipType::Video ? QStringLiteral("video")
                                                                                       : QStringLiteral("image"));
                map.insert(QStringLiteral("mediaName"), media_ && !clip.placeholderEmpty ? media_->name : QString());
                const QString thumb = !clip.thumbnailPath.isEmpty() ? clip.thumbnailPath : clip.path;
                map.insert(QStringLiteral("thumbnail"),
                           thumb.isEmpty() ? QString() : QUrl::fromLocalFile(thumb).toString());
                media.append({clip.timelineStart, t, map});
            }
        }
    }
    const auto byTime = [](const Slot &a, const Slot &b) {
        return a.start != b.start ? a.start < b.start : a.track > b.track;
    };
    std::sort(media.begin(), media.end(), byTime);
    std::sort(texts.begin(), texts.end(), byTime);
    QVariantList mediaList;
    int emptyCount = 0;
    for (int i = 0; i < media.size(); ++i) {
        media[i].map.insert(QStringLiteral("number"), i + 1);
        emptyCount += media.at(i).map.value(QStringLiteral("empty")).toBool() ? 1 : 0;
        mediaList.append(media.at(i).map);
    }
    QVariantList textList;
    for (const Slot &slot : texts)
        textList.append(slot.map);
    return QVariantMap{
        {QStringLiteral("assetId"), asset->id},
        {QStringLiteral("name"), asset->generator.value(QStringLiteral("templateName")).toString()},
        {QStringLiteral("slots"), mediaList},
        {QStringLiteral("texts"), textList},
        {QStringLiteral("emptySlots"), emptyCount},
    };
}

bool AppController::fillTemplateSlotWithAsset(const QString &slotClipId, const QString &mediaAssetId,
                                              bool recordUndo)
{
    const drift::MediaAsset *media = m_project.asset(mediaAssetId);
    if (!media || (media->kind != drift::MediaKind::Image && media->kind != drift::MediaKind::Video)) {
        setLastMessage(tr("A slot takes a photo or a video"), QStringLiteral("warning"));
        return false;
    }
    drift::Project before;
    if (recordUndo)
        before = m_project.detachedCopy();
    const drift::Clip *picked = findClipAnywhere(m_project, slotClipId);
    if (!picked || picked->placeholderId.isEmpty())
        return false;
    const QString placeholderId = picked->placeholderId;

    // A slot may show up more than once (a picture repeated on the beat): every clip of it, in the
    // same template, takes the picture.
    QList<drift::Clip *> targets;
    m_project.forEachTrackList([&](QList<drift::Track> &tracks) {
        bool here = false;
        for (const drift::Track &track : tracks) {
            for (const drift::Clip &clip : track.clips)
                here = here || clip.id == slotClipId;
        }
        if (!here)
            return;
        for (drift::Track &track : tracks) {
            for (drift::Clip &clip : track.clips) {
                if (clip.placeholderId == placeholderId && clip.type != drift::ClipType::Text)
                    targets.append(&clip);
            }
        }
    });

    QSet<QString> standIns;
    for (drift::Clip *clip : std::as_const(targets)) {
        if (clip->placeholderEmpty && clip->assetId != mediaAssetId)
            standIns.insert(clip->assetId);
        clip->assetId = media->id;
        clip->type = media->kind == drift::MediaKind::Video ? drift::ClipType::Video : drift::ClipType::Image;
        clip->name = media->name;
        clip->path = media->path;
        clip->thumbnailPath = media->thumbnailPath.isEmpty() ? media->path : media->thumbnailPath;
        clip->filmstripPath = media->filmstripPath;
        clip->rotationCorrection = drift::rotationCorrectionOf(*media);
        clip->faceTrackPath.clear();
        clip->depthPath.clear();
        clip->placeholderEmpty = false;
        // Fill the slot's box without stretching: the middle of the picture, cut on its long side.
        QSizeF mediaSize(media->width, media->height);
        if (clip->rotationCorrection == 90 || clip->rotationCorrection == 270)
            mediaSize.transpose();
        clip->sourceFrame = drift::coverSourceFrame(mediaSize, slotSize(*clip, m_project.width(), m_project.height()),
                                                    media->sourceFrame);
        clip->reverse = false;
        clip->speedCurve = {};
        clip->srcIn = 0;
        if (clip->type == drift::ClipType::Video && media->durationUs > 0) {
            // A clip shorter than its slot is slowed to cover it rather than leaving a hole.
            clip->speed = media->durationUs >= clip->timelineDuration
                              ? 1.0
                              : qMax(0.1, double(media->durationUs) / double(clip->timelineDuration));
            clip->srcOut = qMin<drift::TimeUs>(media->durationUs, clip->sourceSpanUs());
        } else {
            clip->speed = 1.0;
            clip->srcOut = clip->timelineDuration;
        }
    }

    // The stand-in pictures go once nothing shows them any more.
    for (const QString &oldAssetId : std::as_const(standIns)) {
        bool used = false;
        m_project.forEachTrackList([&](QList<drift::Track> &tracks) {
            for (const drift::Track &track : tracks) {
                for (const drift::Clip &other : track.clips)
                    used = used || other.assetId == oldAssetId;
            }
        });
        if (!used) {
            m_project.assets().remove(oldAssetId);
            m_project.assetOrder().removeAll(oldAssetId);
        }
    }
    if (m_assetLibrary)
        m_assetLibrary->syncToProject();
    if (recordUndo) {
        pushProjectEdit(before, tr("Fill template"));
        finishEdit(QString());
    }
    return true;
}

bool AppController::fillTemplateSlot(const QString &slotClipId, const QString &mediaAssetId)
{
    return fillTemplateSlotWithAsset(slotClipId, mediaAssetId, true);
}

int AppController::fillTemplateSlotsFromUrls(const QString &compositeAssetId, const QString &firstSlotClipId,
                                             const QList<QUrl> &urls)
{
    if (!m_assetLibrary || urls.isEmpty())
        return 0;
    QStringList paths;
    for (const QUrl &url : urls) {
        const QString path = url.isLocalFile() ? url.toLocalFile() : url.toString();
        if (AssetLibrary::isImagePath(path) || AssetLibrary::isVideoPath(path))
            paths.append(path);
    }
    if (paths.isEmpty()) {
        setLastMessage(tr("A slot takes a photo or a video"), QStringLiteral("warning"));
        return 0;
    }

    // The clicked slot first, then the empty ones after it in order.
    const QVariantList slotList = sceneTemplateInfo(compositeAssetId).value(QStringLiteral("slots")).toList();
    QStringList targets;
    bool reached = firstSlotClipId.isEmpty();
    for (const QVariant &value : slotList) {
        const QVariantMap slot = value.toMap();
        const QString clipId = slot.value(QStringLiteral("clipId")).toString();
        if (clipId == firstSlotClipId) {
            reached = true;
            targets.append(clipId);
            continue;
        }
        if (reached && slot.value(QStringLiteral("empty")).toBool())
            targets.append(clipId);
    }
    if (targets.isEmpty())
        return 0;

    const QStringList assetIds = m_assetLibrary->importLocalPaths(paths);
    const int count = qMin(targets.size(), assetIds.size());
    QList<QPair<QString, QString>> fills;
    for (int i = 0; i < count; ++i)
        fills.append({targets.at(i), assetIds.at(i)});

    // A fresh import is probed off the GUI thread; its size and length arrive a moment later, and
    // the cut that fits the slot needs both. Each fill waits for its own asset.
    auto pending = std::make_shared<QList<QPair<QString, QString>>>();
    const drift::Project before = m_project.detachedCopy();
    bool changed = false;
    for (const auto &fill : std::as_const(fills)) {
        if (m_assetLibrary->isImportPending(fill.second))
            pending->append(fill);
        else
            changed = fillTemplateSlotWithAsset(fill.first, fill.second, false) || changed;
    }
    if (changed) {
        pushProjectEdit(before, tr("Fill template"));
        finishEdit(QString());
    }
    if (!pending->isEmpty()) {
        auto connection = std::make_shared<QMetaObject::Connection>();
        *connection = connect(m_assetLibrary, &AssetLibrary::assetMetadataChanged, this,
                              [this, pending, connection](const QString &assetId) {
                                  for (int i = pending->size() - 1; i >= 0; --i) {
                                      if (pending->at(i).second != assetId
                                          || m_assetLibrary->isImportPending(assetId))
                                          continue;
                                      fillTemplateSlotWithAsset(pending->at(i).first, assetId, true);
                                      pending->removeAt(i);
                                  }
                                  if (pending->isEmpty())
                                      disconnect(*connection);
                              });
    }
    return count;
}

bool AppController::setTemplateText(const QString &textClipId, const QString &text)
{
    drift::Clip *probe = findClipAnywhere(m_project, textClipId);
    if (!probe || probe->placeholderId.isEmpty() || probe->textContent == text)
        return false;
    const drift::Project before = m_project.detachedCopy();
    drift::Clip *clip = findClipAnywhere(m_project, textClipId);
    clip->textContent = text;
    pushProjectEdit(before, tr("Template text"));
    finishEdit(QString());
    return true;
}
