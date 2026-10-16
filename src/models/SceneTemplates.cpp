// Scene templates (CapCut-style): insert a packaged little edit as one composition, list its
// slots and texts, and fill them. See engine/SceneTemplateCatalog.h for the package format.

#include "AppController.h"

#include "AssetLibrary.h"
#include "MarketClient.h"
#include "MediaBinController.h"
#include "McpDetail.h"
#include "core/SceneTemplateLayout.h"
#include "core/SceneTemplateTools.h"
#include "engine/AudioOnsets.h"
#include "engine/MediaProbe.h"
#include "engine/FrameCompositor.h"
#include "engine/GpuCompositor.h"
#include "engine/SceneTemplateCatalog.h"

#include <QCryptographicHash>
#include <QDateTime>
#include <QFontDatabase>
#include <QLocale>
#include <QDir>
#include <QFile>
#include <QFileInfo>
#include <QImage>
#include <QImageReader>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <QLinearGradient>
#include <QPainter>
#include <QPainterPath>
#include <QPointer>
#include <QSet>
#include <QSettings>
#include <QStandardPaths>
#include <QUrl>
#include <QUuid>
#include <QtConcurrent>

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

// placeholderId -> the text as the template's package has it, cached by file and time.
QHash<QString, QString> originalTemplateTexts(const QString &templateId)
{
    struct Cached
    {
        QDateTime modified;
        QHash<QString, QString> texts;
    };
    static QHash<QString, Cached> cache;
    const SceneTemplateEntry *entry = templateId.isEmpty() ? nullptr : sceneTemplateForId(templateId);
    if (!entry)
        return {};
    const QDateTime modified = QFileInfo(entry->projectPath).lastModified();
    const auto it = cache.constFind(entry->projectPath);
    if (it != cache.constEnd() && it->modified == modified)
        return it->texts;
    QHash<QString, QString> texts;
    QFile file(entry->projectPath);
    if (file.open(QIODevice::ReadOnly)) {
        const QJsonObject root = QJsonDocument::fromJson(file.readAll()).object();
        for (const QJsonValue &track : root.value(QStringLiteral("tracks")).toArray()) {
            for (const QJsonValue &value : track.toObject().value(QStringLiteral("clips")).toArray()) {
                const QJsonObject clip = value.toObject();
                const QString slot = clip.value(QStringLiteral("placeholderId")).toString();
                const QString type = clip.value(QStringLiteral("type")).toString();
                if (slot.isEmpty() || (type != QLatin1String("text") && type != QLatin1String("subtitle")))
                    continue;
                QString text = clip.value(QStringLiteral("textContent")).toString();
                if (text.isEmpty())
                    text = clip.value(QStringLiteral("name")).toString();
                texts.insert(slot, text);
            }
        }
    }
    cache.insert(entry->projectPath, {modified, texts});
    return texts;
}

void containInBox(drift::Clip &clip, const QSizeF &media, int canvasW, int canvasH)
{
    const auto single = [](const drift::KeyframeTrack<double> &track) { return track.keyframes().size() <= 1; };
    if (media.isEmpty() || !single(clip.transformX) || !single(clip.transformY) || !single(clip.transformW)
        || !single(clip.transformH)) {
        return;
    }
    const double x = clip.transformX.isEmpty() ? 0.0 : clip.transformX.evaluateAt(0);
    const double y = clip.transformY.isEmpty() ? 0.0 : clip.transformY.evaluateAt(0);
    const double w = clip.transformW.isEmpty() ? canvasW : clip.transformW.evaluateAt(0);
    const double h = clip.transformH.isEmpty() ? canvasH : clip.transformH.evaluateAt(0);
    const double scale = qMin(w / media.width(), h / media.height());
    const double nw = media.width() * scale;
    const double nh = media.height() * scale;
    const auto put = [](drift::KeyframeTrack<double> &track, double value) {
        track.setKeyframe(track.keyframes().isEmpty() ? 0 : track.keyframes().firstKey(), value);
    };
    put(clip.transformX, x + (w - nw) / 2.0);
    put(clip.transformY, y + (h - nh) / 2.0);
    put(clip.transformW, nw);
    put(clip.transformH, nh);
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

void AppController::setMarketClient(MarketClient *client)
{
    if (m_marketClient) {
        disconnect(m_marketClient, nullptr, this, nullptr);
        m_marketClient->setStockInstaller({});
    }
    m_marketClient = client;
    if (!client)
        return;
    connect(client, &MarketClient::sceneTemplateReady, this, [this](const QString &templateId, bool use) {
        emit sceneTemplatesChanged();
        if (!use)
            return;
        // Asked for from "Use with my photos" or "Change template": it goes in with that.
        const bool pending = m_pendingTemplateId == templateId;
        const QList<QUrl> urls = pending ? m_pendingTemplateUrls : QList<QUrl>();
        const QString swap = pending ? m_pendingTemplateSwap : QString();
        if (pending) {
            m_pendingTemplateId.clear();
            m_pendingTemplateUrls.clear();
            m_pendingTemplateSwap.clear();
        }
        if (!swap.isEmpty())
            swapSceneTemplate(swap, templateId);
        else if (!urls.isEmpty())
            insertSceneTemplateWithMedia(templateId, urls);
        else
            insertSceneTemplate(templateId);
    });
    // LUTs, looks, text styles and animations, transitions and shapes from Stock.
    QPointer<AppController> self(this);
    client->setStockInstaller([self](const QString &delivery, const QString &path, const QString &title,
                                     const MarketClient::InstallDone &done) {
        if (!self) {
            done(false, QString(), QString(), QStringLiteral("the editor is gone"));
            return;
        }
        self->installStockFile(delivery, path, title, done);
    });
    connect(client, &MarketClient::favoritesFetched, this, &AppController::mergeAccountFavorites);
    connect(client, &MarketClient::favoritesPushed, this, [](const QDateTime &updatedAt) {
        QSettings settings;
        settings.setValue(QStringLiteral("assetFavoritesSync/dirty"), false);
        if (updatedAt.isValid())
            settings.setValue(QStringLiteral("assetFavoritesSync/at"), updatedAt);
    });
}

void AppController::mergeAccountFavorites(const QVariantMap &server, const QDateTime &updatedAt)
{
    QSettings settings;
    const QDateTime lastSync = settings.value(QStringLiteral("assetFavoritesSync/at")).toDateTime();
    const bool dirty = settings.value(QStringLiteral("assetFavoritesSync/dirty"), false).toBool();
    QHash<QString, QSet<QString>> fromServer;
    for (auto it = server.cbegin(); it != server.cend(); ++it) {
        const QStringList ids = it.value().toStringList();
        if (!it.key().isEmpty() && !ids.isEmpty())
            fromServer.insert(it.key(), QSet<QString>(ids.cbegin(), ids.cend()));
    }

    // Never synced from here, or changed here since: keep both sides and send the union. Synced
    // and unchanged here: the account is newer, so it wins (a favorite removed on another
    // computer goes here too).
    const bool takeServer = lastSync.isValid() && !dirty && (!updatedAt.isValid() || updatedAt > lastSync);
    const bool nothingNew = lastSync.isValid() && !dirty && updatedAt.isValid() && updatedAt <= lastSync;
    if (nothingNew)
        return;
    QHash<QString, QSet<QString>> merged = takeServer ? fromServer : m_assetFavorites;
    if (!takeServer) {
        for (auto it = fromServer.cbegin(); it != fromServer.cend(); ++it)
            merged[it.key()].unite(it.value());
    }
    const QStringList tabs = QStringList(m_assetFavorites.keyBegin(), m_assetFavorites.keyEnd())
                             + QStringList(merged.keyBegin(), merged.keyEnd());
    m_assetFavorites = merged;
    for (const QString &tab : tabs)
        saveAssetFavorites(tab);
    emit assetFavoritesChanged();
    if (takeServer) {
        if (updatedAt.isValid())
            settings.setValue(QStringLiteral("assetFavoritesSync/at"), updatedAt);
        return;
    }
    settings.setValue(QStringLiteral("assetFavoritesSync/dirty"), true);
    if (m_marketClient)
        m_marketClient->pushFavorites(assetFavoritesMap());
}

QVariantMap AppController::assetFavoritesMap() const
{
    QVariantMap out;
    for (auto it = m_assetFavorites.cbegin(); it != m_assetFavorites.cend(); ++it) {
        if (it.key().isEmpty() || it.value().isEmpty())
            continue;
        QStringList ids(it.value().cbegin(), it.value().cend());
        ids.sort();
        out.insert(it.key(), ids);
    }
    return out;
}

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
            {QStringLiteral("mine"), entry.origin == QLatin1String("user")},
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

QString AppController::sceneTemplateCategoryLabelFor(const QString &categoryId) const
{
    return sceneTemplateCategoryLabel(categoryId);
}

QString AppController::insertSceneTemplate(const QString &templateId)
{
    return placeSceneTemplate(templateId, true, true);
}

QString AppController::placeSceneTemplate(const QString &templateId, bool recordUndo, bool allowResize)
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
    if (allowResize && timelineEmpty
        && (m_project.width() != content.width() || m_project.height() != content.height()))
        m_project.setResolution(content.width(), content.height());

    QList<drift::Track> tracks = content.tracks();
    drift::scaleTemplateLayout(tracks, content.width(), content.height(), m_project.width(), m_project.height());

    // My brand: Business templates, and any that mark a brand role or a logo slot, take the kit's
    // colours and font now and its logo once the slots exist.
    QStringList logoSlots;
    {
        const drift::BrandKit kit = currentBrandKit();
        if (!kit.isEmpty() && brandKitAutoApply() && templateWantsBrand(entry->category, entry->tags, tracks))
            logoSlots = drift::applyBrandKit(tracks, kit).logoSlots;
    }

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
    // Slots are numbered in the order they appear, as the Fill template panel lists them (by time,
    // then bottom track first), so the stand-in showing "3" is the panel's slot 3.
    QHash<QString, int> slotNumbers;
    {
        struct First
        {
            drift::TimeUs start;
            int track;
            QString id;
        };
        QHash<QString, First> firsts;
        for (int t = 0; t < tracks.size(); ++t) {
            for (const drift::Clip &clip : tracks.at(t).clips) {
                if (clip.placeholderId.isEmpty() || clip.type == drift::ClipType::Text
                    || clip.type == drift::ClipType::Subtitle)
                    continue;
                auto it = firsts.find(clip.placeholderId);
                if (it == firsts.end() || clip.timelineStart < it->start)
                    firsts.insert(clip.placeholderId, {clip.timelineStart, t, clip.placeholderId});
            }
        }
        QList<First> order = firsts.values();
        std::sort(order.begin(), order.end(), [](const First &a, const First &b) {
            return a.start != b.start ? a.start < b.start : a.track > b.track;
        });
        for (int i = 0; i < order.size(); ++i)
            slotNumbers.insert(order.at(i).id, i + 1);
    }
    const int slotNumber = int(slotNumbers.size());
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
                const int number = slotNumbers.value(clip.placeholderId);
                const QSizeF box = slotSize(clip, m_project.width(), m_project.height());
                drift::MediaAsset picture;
                picture.kind = drift::MediaKind::Image;
                picture.name = clip.placeholderLabel.isEmpty() ? tr("Slot %1").arg(number) : clip.placeholderLabel;
                picture.path = slotPicture(box, number, tr("Your photo or video here"));
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
                    clip.placeholderLabel = tr("Photo %1").arg(number);
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
    if (timelineEmpty) {
        int own = -1;
        int target = -1;
        for (int t = 0; t < m_project.tracks().size(); ++t) {
            const drift::Track &track = m_project.tracks().at(t);
            for (const drift::Clip &clip : track.clips) {
                if (clip.id == compositeId)
                    own = t;
            }
            if (target < 0 && track.clips.isEmpty() && track.type == drift::TrackType::Video
                && !track.isAdjustment())
                target = t;
        }
        if (own >= 0 && target >= 0 && m_project.tracks().at(own).clips.size() == 1) {
            m_project.tracks()[target].clips.append(m_project.tracks().at(own).clips.first());
            m_project.tracks().removeAt(own);
        }
    }
    drift::Clip *composite = findClipAnywhere(m_project, compositeId);
    if (composite) {
        if (drift::MediaAsset *asset = m_project.asset(composite->assetId)) {
            asset->generator = QJsonObject{
                {QStringLiteral("kind"), kSceneTemplateKind},
                {QStringLiteral("templateId"), entry->id},
                {QStringLiteral("templateName"), entry->displayName},
                {QStringLiteral("binFolderId"), folder.id},
            };
        }
    }
    if (m_assetLibrary)
        m_assetLibrary->syncToProject();
    if (composite && !logoSlots.isEmpty()) {
        if (const drift::MediaAsset *asset = m_project.asset(composite->assetId))
            fillLogoSlots(asset->sequenceId, logoSlots);
    }
    if (!recordUndo)
        return compositeId;
    pushProjectEdit(before, tr("Add template"));
    finishEdit(QString());
    const QStringList missingFonts = missingTemplateFonts(tracks);
    if (!missingFonts.isEmpty()) {
        // It still goes in: the text falls back to another font until these are installed.
        setLastMessage(tr("Template added, but it uses fonts this computer does not have: %1. Install the "
                          "Fonts packs from Extras so it looks as designed.").arg(missingFonts.join(QStringLiteral(", "))),
                       QStringLiteral("warning"));
        selectClipById(compositeId);
        emit sequenceTabsChanged();
        return compositeId;
    }
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
                map.insert(QStringLiteral("pixelSize"), clip.textStyle.pixelSize);
                texts.append({clip.timelineStart, t, map});
            } else if (seenSlots.contains(clip.placeholderId)) {
                continue; // a repeat of a slot already listed: one fill fills them all
            } else {
                seenSlots.insert(clip.placeholderId);
                const drift::MediaAsset *media_ = m_project.asset(clip.assetId);
                map.insert(QStringLiteral("empty"), clip.placeholderEmpty);
                map.insert(QStringLiteral("assetId"), clip.placeholderEmpty ? QString() : clip.assetId);
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
    // The form names each text by what it is for: the original text says it best ("+51 999…" is
    // a phone even after the user typed theirs), else what it says now.
    const QHash<QString, QString> originals = originalTemplateTexts(asset->generator.value(QStringLiteral("templateId")).toString());
    int largest = 0;
    for (const Slot &slot : texts)
        largest = qMax(largest, slot.map.value(QStringLiteral("pixelSize")).toInt());
    QHash<QString, int> kindCount;
    QVariantList textList;
    for (Slot &slot : texts) {
        const QString current = slot.map.value(QStringLiteral("text")).toString();
        const QString slotId = slot.map.value(QStringLiteral("slotId")).toString();
        // A template no longer installed has no sample to compare with: count its texts as the user's.
        const bool known = originals.contains(slotId);
        const QString original = originals.value(slotId, current);
        const bool isLargest = largest > 0 && slot.map.value(QStringLiteral("pixelSize")).toInt() >= largest;
        const QString kind = drift::guessTemplateTextKind(original, slot.map.value(QStringLiteral("label")).toString(),
                                                          isLargest);
        const int n = ++kindCount[kind];
        slot.map.insert(QStringLiteral("kind"), kind);
        slot.map.insert(QStringLiteral("original"), original);
        slot.map.insert(QStringLiteral("edited"), known ? current != original : !current.isEmpty());
        slot.map.insert(QStringLiteral("kindIndex"), n);
        textList.append(slot.map);
    }
    // "Title", "Title 2"…: a number only when a kind repeats.
    for (QVariant &value : textList) {
        QVariantMap map = value.toMap();
        const QString kind = map.value(QStringLiteral("kind")).toString();
        QString label = templateTextKindLabel(kind);
        if (kindCount.value(kind) > 1)
            label = QStringLiteral("%1 %2").arg(label).arg(map.value(QStringLiteral("kindIndex")).toInt());
        map.insert(QStringLiteral("fieldLabel"), label);
        value = map;
    }

    QString musicName;
    bool hasMusic = false;
    for (const drift::Track &track : tracks) {
        if (track.type != drift::TrackType::Audio)
            continue;
        for (const drift::Clip &clip : track.clips) {
            if (hasMusic)
                break;
            hasMusic = true;
            const drift::MediaAsset *music = m_project.asset(clip.assetId);
            musicName = music ? music->name : clip.name;
        }
    }
    return QVariantMap{
        {QStringLiteral("assetId"), asset->id},
        {QStringLiteral("templateId"), asset->generator.value(QStringLiteral("templateId")).toString()},
        {QStringLiteral("name"), asset->generator.value(QStringLiteral("templateName")).toString()},
        {QStringLiteral("slots"), mediaList},
        {QStringLiteral("texts"), textList},
        {QStringLiteral("emptySlots"), emptyCount},
        {QStringLiteral("hasMusic"), hasMusic},
        {QStringLiteral("musicName"), musicName},
        {QStringLiteral("inside"), m_project.activeSequenceId() == asset->sequenceId},
    };
}

bool AppController::fillTemplateSlotWithAsset(const QString &slotClipId, const QString &mediaAssetId,
                                              bool recordUndo, bool contain)
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
        clip->poseTrackPath.clear();
        clip->depthPath.clear();
        clip->placeholderEmpty = false;
        // Fill the slot's box without stretching: the middle of the picture, cut on its long side.
        QSizeF mediaSize(media->width, media->height);
        if (clip->rotationCorrection == 90 || clip->rotationCorrection == 270)
            mediaSize.transpose();
        if (contain) {
            // A logo is shown whole, fitted inside the slot's box, never cut.
            clip->sourceFrame = media->sourceFrame.isValid() ? media->sourceFrame : QRectF(0, 0, 1, 1);
            containInBox(*clip,
                         QSizeF(mediaSize.width() * clip->sourceFrame.width(),
                                mediaSize.height() * clip->sourceFrame.height()),
                         m_project.width(), m_project.height());
        } else {
            clip->sourceFrame = drift::coverSourceFrame(
                mediaSize, slotSize(*clip, m_project.width(), m_project.height()), media->sourceFrame);
        }
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

// --- Templates of one's own ------------------------------------------------------------------

namespace {

bool isTextKind(drift::ClipType type)
{
    return type == drift::ClipType::Text || type == drift::ClipType::Subtitle;
}

bool isMediaSlotKind(drift::ClipType type)
{
    return type == drift::ClipType::Image || type == drift::ClipType::Video;
}

// "Mi reel de viaje" -> "mi-reel-de-viaje": the readable part of a user template's id.
QString slugFor(const QString &name)
{
    QString s = name.normalized(QString::NormalizationForm_D).toLower();
    QString out;
    for (const QChar c : s) {
        if (c.isLetterOrNumber() && c.unicode() < 128)
            out.append(c);
        else if ((c.isSpace() || c == QLatin1Char('-') || c == QLatin1Char('_')) && !out.endsWith(QLatin1Char('-')))
            out.append(QLatin1Char('-'));
    }
    while (out.endsWith(QLatin1Char('-')))
        out.chop(1);
    return out.left(40).isEmpty() ? QStringLiteral("plantilla") : out.left(40);
}

} // namespace

QVariantMap AppController::clipPlaceholderState(int trackIndex, int clipIndex) const
{
    // Slots are marked inside a composition: that is what a template is made of.
    if (m_project.activeSequenceId().isEmpty() || !isValidClipIndex(trackIndex, clipIndex))
        return {};
    const drift::Clip &clip = m_project.tracks().at(trackIndex).clips.at(clipIndex);
    const bool text = isTextKind(clip.type);
    if (!text && !isMediaSlotKind(clip.type) && clip.placeholderId.isEmpty())
        return {};
    return QVariantMap{
        {QStringLiteral("kind"), text ? QStringLiteral("text") : QStringLiteral("media")},
        {QStringLiteral("marked"), !clip.placeholderId.isEmpty()},
        {QStringLiteral("label"), clip.placeholderLabel},
    };
}

bool AppController::setClipPlaceholder(int trackIndex, int clipIndex, bool marked)
{
    if (clipPlaceholderState(trackIndex, clipIndex).isEmpty())
        return false;
    const drift::Project before = m_project.detachedCopy();
    drift::Clip &clip = m_project.tracks()[trackIndex].clips[clipIndex];
    if (marked == !clip.placeholderId.isEmpty())
        return false;
    if (!marked) {
        clip.placeholderId.clear();
        clip.placeholderLabel.clear();
        clip.placeholderEmpty = false;
    } else if (isTextKind(clip.type)) {
        clip.placeholderId = QStringLiteral("t") + QUuid::createUuid().toString(QUuid::Id128).left(8);
        const QString text = clip.textContent.simplified();
        clip.placeholderLabel = text.size() > 24 ? text.left(23) + QChar(0x2026) : text;
        if (clip.placeholderLabel.isEmpty())
            clip.placeholderLabel = tr("Text");
    } else {
        QSet<QString> slotIds;
        for (const drift::Track &track : m_project.tracks()) {
            for (const drift::Clip &other : track.clips) {
                if (!other.placeholderId.isEmpty() && !isTextKind(other.type))
                    slotIds.insert(other.placeholderId);
            }
        }
        clip.placeholderId = QStringLiteral("p") + QUuid::createUuid().toString(QUuid::Id128).left(8);
        clip.placeholderLabel = tr("Photo %1").arg(slotIds.size() + 1);
        clip.placeholderEmpty = false;
    }
    pushProjectEdit(before, marked ? tr("Make slot") : tr("Remove slot"));
    finishEdit(QString());
    return true;
}

QString AppController::clipAssetId(int trackIndex, int clipIndex) const
{
    return isValidClipIndex(trackIndex, clipIndex) ? m_project.tracks().at(trackIndex).clips.at(clipIndex).assetId
                                                   : QString();
}

void AppController::requestSaveTemplate(const QString &compositeAssetId)
{
    const drift::MediaAsset *asset = m_project.asset(compositeAssetId);
    if (!asset || asset->kind != drift::MediaKind::Composite)
        return;
    emit saveTemplateRequested(compositeAssetId, asset->name);
}

QVariantMap AppController::compositeTemplateSummary(const QString &compositeAssetId) const
{
    const drift::MediaAsset *asset = m_project.asset(compositeAssetId);
    if (!asset || asset->kind != drift::MediaKind::Composite)
        return {};
    QSet<QString> slotIds;
    int texts = 0;
    for (const drift::Track &track : m_project.sequenceTracks(asset->sequenceId)) {
        for (const drift::Clip &clip : track.clips) {
            if (clip.placeholderId.isEmpty())
                continue;
            if (isTextKind(clip.type))
                ++texts;
            else
                slotIds.insert(clip.placeholderId);
        }
    }
    return QVariantMap{
        {QStringLiteral("name"), asset->name},
        {QStringLiteral("slots"), int(slotIds.size())},
        {QStringLiteral("texts"), texts},
    };
}

QString AppController::saveCompositeAsTemplate(const QString &compositeAssetId, const QString &name,
                                               const QString &category)
{
    const drift::MediaAsset *composite = m_project.asset(compositeAssetId);
    if (!composite || composite->kind != drift::MediaKind::Composite) {
        setLastMessage(tr("Only a composition can be saved as a template"), QStringLiteral("warning"));
        return {};
    }
    const QString title = name.trimmed().isEmpty() ? composite->name : name.trimmed();
    const QString root = userSceneTemplatesDir();
    const QString id = QStringLiteral("mine-%1-%2").arg(slugFor(title),
                                                      QUuid::createUuid().toString(QUuid::Id128).left(6));
    const QString dir = QDir(root).filePath(id);
    if (root.isEmpty() || !QDir().mkpath(QDir(dir).filePath(QStringLiteral("media")))) {
        setLastMessage(tr("Could not create the template folder"), QStringLiteral("error"));
        return {};
    }

    // The composition's own timeline, with its pictures copied into the package (slots excepted:
    // whoever uses the template brings their own) and its paths made relative.
    drift::Project content;
    content.setResolution(m_project.width(), m_project.height());
    content.setFps(m_project.fps());
    content.tracks() = m_project.sequenceTracks(composite->sequenceId);
    QHash<QString, QString> copied; // asset id -> relative path
    QSet<QString> slotIds;
    int texts = 0;
    int fileNumber = 0;
    for (drift::Track &track : content.tracks()) {
        for (drift::Clip &clip : track.clips) {
            if (!clip.placeholderId.isEmpty()) {
                if (isTextKind(clip.type)) {
                    ++texts;
                    continue;
                }
                slotIds.insert(clip.placeholderId);
                clip.assetId.clear();
                clip.path.clear();
                clip.thumbnailPath.clear();
                clip.filmstripPath.clear();
                clip.faceTrackPath.clear();
                clip.poseTrackPath.clear();
                clip.depthPath.clear();
                clip.sourceFrame = QRectF(0, 0, 1, 1);
                continue;
            }
            if (clip.assetId.isEmpty())
                continue;
            const drift::MediaAsset *media = m_project.asset(clip.assetId);
            if (!media || media->path.isEmpty())
                continue;
            if (!copied.contains(media->id)) {
                const QString rel = QStringLiteral("media/%1-%2").arg(++fileNumber).arg(QFileInfo(media->path).fileName());
                if (!QFile::copy(media->path, QDir(dir).filePath(rel))) {
                    QDir(dir).removeRecursively();
                    setLastMessage(tr("Could not copy %1 into the template").arg(media->name), QStringLiteral("error"));
                    return {};
                }
                drift::MediaAsset packed = *media;
                packed.path = rel;
                packed.thumbnailPath.clear();
                packed.filmstripPath.clear();
                packed.folderId.clear();
                content.addAsset(packed);
                copied.insert(media->id, rel);
            }
            clip.path = copied.value(media->id);
            clip.thumbnailPath.clear();
            clip.filmstripPath.clear();
            clip.faceTrackPath.clear();
            clip.poseTrackPath.clear();
            clip.depthPath.clear();
        }
    }
    {
        QFile file(QDir(dir).filePath(QStringLiteral("project.json")));
        if (!file.open(QIODevice::WriteOnly) || file.write(QJsonDocument(content.toJson(false)).toJson()) <= 0) {
            QDir(dir).removeRecursively();
            setLastMessage(tr("Could not save the template"), QStringLiteral("error"));
            return {};
        }
    }

    // The card: the composition at the middle of its length, as the compositor draws it.
    const drift::TimeUs durationUs = m_project.sequenceDurationUs(composite->sequenceId);
    {
        const drift::Project view = m_project.sequenceView(composite->sequenceId);
        FrameCompositor compositor;
        compositor.setProject(&view);
        FrameCompositor::RenderOptions options;
        options.previewScale = qMin(1.0, 768.0 / qMax(1, qMax(view.width(), view.height())));
        QImage frame = GpuCompositor::isAvailable() ? compositor.compositeAt(durationUs / 2, options) : QImage();
        if (frame.isNull()) {
            frame = QImage(432, 768, QImage::Format_RGB32);
            frame.fill(QColor(0x2b, 0x2f, 0x3d));
        }
        frame.save(QDir(dir).filePath(QStringLiteral("thumbnail.png")));
    }

    const QString locale = QLocale().name().section(QLatin1Char('_'), 0, 0);
    QJsonObject names{{QStringLiteral("en"), title}};
    names.insert(locale.isEmpty() ? QStringLiteral("es") : locale, title);
    const QJsonObject manifest{
        {QStringLiteral("id"), id},
        {QStringLiteral("displayName"), title},
        {QStringLiteral("names"), names},
        {QStringLiteral("category"), category.trimmed().isEmpty() ? QStringLiteral("mine") : category.trimmed()},
        // Ahead of ours: a person's own templates are the first thing they look for.
        {QStringLiteral("order"), -1000},
        {QStringLiteral("width"), m_project.width()},
        {QStringLiteral("height"), m_project.height()},
        {QStringLiteral("durationSec"), drift::usToSeconds(durationUs)},
        {QStringLiteral("slots"), int(slotIds.size())},
        {QStringLiteral("texts"), texts},
        {QStringLiteral("origin"), QStringLiteral("user")},
        {QStringLiteral("createdAt"), QDateTime::currentDateTimeUtc().toString(Qt::ISODate)},
    };
    QFile manifestFile(QDir(dir).filePath(QStringLiteral("template.json")));
    if (!manifestFile.open(QIODevice::WriteOnly) || manifestFile.write(QJsonDocument(manifest).toJson()) <= 0) {
        QDir(dir).removeRecursively();
        setLastMessage(tr("Could not save the template"), QStringLiteral("error"));
        return {};
    }
    manifestFile.close();
    reloadSceneTemplateCatalog();
    emit sceneTemplatesChanged();
    setLastMessage(slotIds.isEmpty()
                       ? tr("Saved in Templates › Scenes. It has no slots yet: open the composition and make "
                            "photos into slots with a right click.")
                       : tr("Saved in Templates › Scenes, with %n slot(s)", "", int(slotIds.size())),
                   slotIds.isEmpty() ? QStringLiteral("warning") : QStringLiteral("info"));
    return id;
}

bool AppController::deleteUserSceneTemplate(const QString &templateId)
{
    const SceneTemplateEntry *entry = sceneTemplateForId(templateId);
    const QString root = userSceneTemplatesDir();
    if (!entry || entry->origin != QLatin1String("user") || root.isEmpty()
        || !QDir::cleanPath(entry->packageDir).startsWith(QDir::cleanPath(root) + QLatin1Char('/'))) {
        return false;
    }
    if (!QDir(entry->packageDir).removeRecursively())
        return false;
    reloadSceneTemplateCatalog();
    emit sceneTemplatesChanged();
    setLastMessage(tr("Template deleted"), QStringLiteral("info"));
    return true;
}

QStringList AppController::missingTemplateFonts(const QList<drift::Track> &tracks)
{
    QSet<QString> wanted;
    for (const drift::Track &track : tracks) {
        for (const drift::Clip &clip : track.clips) {
            if (isTextKind(clip.type) && !clip.textStyle.fontFamily.isEmpty())
                wanted.insert(clip.textStyle.fontFamily);
        }
    }
    const QStringList installed = QFontDatabase::families();
    QStringList missing;
    for (const QString &family : std::as_const(wanted)) {
        if (!installed.contains(family, Qt::CaseInsensitive))
            missing.append(family);
    }
    std::sort(missing.begin(), missing.end());
    return missing;
}

// --- Faster use (0.14.0): with my photos, change template, cuts to the beat, text form, brand ----

namespace {

// The tracks of a timeline wherever they live right now, writable. Null for an unknown id.
QList<drift::Track> *writableSequenceTracks(drift::Project &project, const QString &sequenceId)
{
    if (!project.hasSequence(sequenceId))
        return nullptr;
    const QList<drift::Track> *target = &std::as_const(project).sequenceTracks(sequenceId);
    QList<drift::Track> *found = nullptr;
    project.forEachTrackList([&](QList<drift::Track> &tracks) {
        if (&tracks == target)
            found = &tracks;
    });
    return found;
}

// A picture's or a video's size as it shows (rotation applied), without importing it.
QSize displayedSize(const QString &path)
{
    if (AssetLibrary::isImagePath(path)) {
        QImageReader reader(path);
        reader.setAutoTransform(true);
        QSize size = reader.size();
        if (reader.transformation() & QImageIOHandler::TransformationRotate90)
            size.transpose();
        return size;
    }
    const MediaInfo info = MediaProbe::probe(path);
    for (const StreamInfo &stream : info.streams) {
        if (stream.type != StreamInfo::Type::Video || stream.attachedPicture)
            continue;
        QSize size(stream.width, stream.height);
        if (stream.rotationDegrees == 90 || stream.rotationDegrees == 270)
            size.transpose();
        return size;
    }
    return {};
}

QVariantList sortedSuggestions(const QVariantList &templates, int count, const QString &shape,
                               const QString &projectShape, const QString &excludeId)
{
    QList<QPair<double, QVariantMap>> scored;
    for (const QVariant &value : templates) {
        QVariantMap t = value.toMap();
        if (t.value(QStringLiteral("id")).toString() == excludeId)
            continue;
        const QString tShape = drift::shapeOfSize(t.value(QStringLiteral("width")).toInt(),
                                                  t.value(QStringLiteral("height")).toInt());
        const double score = drift::sceneTemplateMatchScore(t.value(QStringLiteral("slots")).toInt(), tShape, count,
                                                            shape, projectShape);
        if (score < 0)
            continue;
        t.insert(QStringLiteral("score"), score);
        t.insert(QStringLiteral("shape"), tShape);
        scored.append({score, t});
    }
    std::stable_sort(scored.begin(), scored.end(),
                     [](const auto &a, const auto &b) { return a.first > b.first; });
    QVariantList out;
    for (int i = 0; i < scored.size() && i < 36; ++i)
        out.append(scored.at(i).second);
    return out;
}

const QLatin1String kBrandGroup("brandKit");

} // namespace

QString AppController::templateTextKindLabel(const QString &kind)
{
    if (kind == QLatin1String("business"))
        return tr("Business name");
    if (kind == QLatin1String("phone"))
        return tr("Phone");
    if (kind == QLatin1String("price"))
        return tr("Price");
    if (kind == QLatin1String("discount"))
        return tr("Discount");
    if (kind == QLatin1String("date"))
        return tr("Date");
    if (kind == QLatin1String("time"))
        return tr("Hours");
    if (kind == QLatin1String("web"))
        return tr("Website");
    if (kind == QLatin1String("email"))
        return tr("Email");
    if (kind == QLatin1String("handle"))
        return tr("Social media user");
    if (kind == QLatin1String("address"))
        return tr("Address");
    if (kind == QLatin1String("cta"))
        return tr("Call to action");
    if (kind == QLatin1String("title"))
        return tr("Title");
    if (kind == QLatin1String("subtitle"))
        return tr("Subtitle");
    return tr("Text");
}

// --- Use with my photos ---------------------------------------------------------------------

QVariantMap AppController::suggestSceneTemplatesForMedia(const QList<QUrl> &urls) const
{
    int vertical = 0;
    int horizontal = 0;
    int square = 0;
    int count = 0;
    for (const QUrl &url : urls) {
        const QString path = url.isLocalFile() ? url.toLocalFile() : url.toString();
        if (!AssetLibrary::isImagePath(path) && !AssetLibrary::isVideoPath(path))
            continue;
        ++count;
        const QSize size = displayedSize(path);
        const QString shape = drift::shapeOfSize(size.width(), size.height());
        vertical += shape == QLatin1String("vertical") ? 1 : 0;
        horizontal += shape == QLatin1String("horizontal") ? 1 : 0;
        square += shape == QLatin1String("square") ? 1 : 0;
    }
    bool timelineEmpty = true;
    for (const drift::Track &track : m_project.rootTracks())
        timelineEmpty = timelineEmpty && track.clips.isEmpty();
    const QString projectShape = timelineEmpty ? QString() : drift::shapeOfSize(m_project.width(), m_project.height());
    const QString shape = drift::majorityShape(vertical, horizontal, square);
    const QString bucket = drift::photoCountBucket(count);
    return QVariantMap{
        {QStringLiteral("count"), count},
        {QStringLiteral("shape"), shape},
        // What Stock is asked for: the shape the result will have (the project's, once it has one).
        {QStringLiteral("stockShape"), projectShape.isEmpty() ? shape : projectShape},
        {QStringLiteral("bucket"), bucket},
        {QStringLiteral("nextBucket"), drift::nextPhotoCountBucket(bucket)},
        {QStringLiteral("installed"), sortedSuggestions(sceneTemplates(), count, shape, projectShape, {})},
    };
}

QVariantMap AppController::suggestSceneTemplatesForSwap(const QString &compositeAssetId) const
{
    const QVariantMap info = sceneTemplateInfo(compositeAssetId);
    if (info.isEmpty())
        return {};
    const QVariantList slotList = info.value(QStringLiteral("slots")).toList();
    const int filled = int(slotList.size()) - info.value(QStringLiteral("emptySlots")).toInt();
    const int count = filled > 0 ? filled : int(slotList.size());
    const QString shape = drift::shapeOfSize(m_project.width(), m_project.height());
    const QString bucket = drift::photoCountBucket(count);
    return QVariantMap{
        {QStringLiteral("count"), count},
        {QStringLiteral("shape"), shape},
        {QStringLiteral("stockShape"), shape},
        {QStringLiteral("bucket"), bucket},
        {QStringLiteral("nextBucket"), drift::nextPhotoCountBucket(bucket)},
        {QStringLiteral("currentId"), info.value(QStringLiteral("templateId"))},
        {QStringLiteral("installed"),
         sortedSuggestions(sceneTemplates(), count, shape, shape, info.value(QStringLiteral("templateId")).toString())},
    };
}

QString AppController::insertSceneTemplateWithMedia(const QString &templateId, const QList<QUrl> &urls)
{
    const QString compositeId = insertSceneTemplate(templateId);
    if (compositeId.isEmpty() || urls.isEmpty())
        return compositeId;
    const drift::Clip *composite = findClipAnywhere(m_project, compositeId);
    const QString assetId = composite ? composite->assetId : QString();
    const int slotCount = int(sceneTemplateInfo(assetId).value(QStringLiteral("slots")).toList().size());
    const int filled = fillTemplateSlotsFromUrls(assetId, QString(), urls);
    int media = 0;
    for (const QUrl &url : urls) {
        const QString path = url.isLocalFile() ? url.toLocalFile() : url.toString();
        media += AssetLibrary::isImagePath(path) || AssetLibrary::isVideoPath(path) ? 1 : 0;
    }
    if (media > filled && filled > 0) {
        setLastMessage(tr("Template added with %n of your photos. The rest did not fit: it has %1 slot(s).", "", filled)
                           .arg(slotCount),
                       QStringLiteral("info"));
    } else if (filled > 0) {
        setLastMessage(slotCount > filled
                           ? tr("Template added with your %n photo(s). Fill the other slots in the panel on the right.",
                                "", filled)
                           : tr("Template added with your %n photo(s)", "", filled),
                       QStringLiteral("info"));
    }
    return compositeId;
}

void AppController::useStockSceneTemplate(const QString &itemId, const QString &title, const QList<QUrl> &urls,
                                          const QString &swapAssetId)
{
    if (!m_marketClient)
        return;
    m_pendingTemplateId = m_marketClient->sceneTemplateIdForItem(itemId);
    m_pendingTemplateUrls = urls;
    m_pendingTemplateSwap = swapAssetId;
    m_marketClient->useSceneTemplate(itemId, title);
}

// --- Change template --------------------------------------------------------------------------

QString AppController::swapSceneTemplate(const QString &compositeAssetId, const QString &templateId)
{
    const drift::MediaAsset *oldAsset = m_project.asset(compositeAssetId);
    if (!oldAsset || sceneGenerator(*oldAsset).isEmpty())
        return {};
    if (!m_project.activeSequenceId().isEmpty()) {
        setLastMessage(tr("Templates are changed on the main timeline: close the composition first"),
                       QStringLiteral("warning"));
        return {};
    }
    if (!sceneTemplateForId(templateId)) {
        setLastMessage(tr("That template is not installed"), QStringLiteral("warning"));
        return {};
    }
    // The instance to replace: the selected one, else the first on the timeline.
    int t = -1;
    int c = -1;
    if (isValidClipIndex(m_selectedTrack, m_selectedClip)
        && m_project.tracks().at(m_selectedTrack).clips.at(m_selectedClip).assetId == compositeAssetId) {
        t = m_selectedTrack;
        c = m_selectedClip;
    }
    for (int i = 0; t < 0 && i < m_project.tracks().size(); ++i) {
        for (int j = 0; j < m_project.tracks().at(i).clips.size(); ++j) {
            if (m_project.tracks().at(i).clips.at(j).assetId == compositeAssetId) {
                t = i;
                c = j;
                break;
            }
        }
    }
    if (t < 0) {
        setLastMessage(tr("Put the template on the timeline first"), QStringLiteral("warning"));
        return {};
    }

    // What the user put in: pictures by slot number, and the texts they changed.
    const QVariantMap oldInfo = sceneTemplateInfo(compositeAssetId);
    QStringList pictures;
    for (const QVariant &value : oldInfo.value(QStringLiteral("slots")).toList()) {
        const QString assetId = value.toMap().value(QStringLiteral("assetId")).toString();
        if (!assetId.isEmpty())
            pictures.append(assetId);
    }
    const QVariantList oldTexts = oldInfo.value(QStringLiteral("texts")).toList();
    const QString oldFolderId = oldAsset->generator.value(QStringLiteral("binFolderId")).toString();

    setPlaying(false);
    const drift::Project before = m_project.detachedCopy();
    const drift::Clip oldClip = m_project.tracks().at(t).clips.at(c);
    const QString oldTrackId = m_project.tracks().at(t).id;
    {
        drift::Track &track = m_project.tracks()[t];
        track.clips.removeAt(c);
        for (int i = int(track.transitions.size()) - 1; i >= 0; --i) {
            if (track.transitions.at(i).fromClipId == oldClip.id || track.transitions.at(i).toClipId == oldClip.id)
                track.transitions.removeAt(i);
        }
    }
    const drift::TimeUs playhead = m_playheadUs;
    m_playheadUs = oldClip.timelineStart;
    const QString newClipId = placeSceneTemplate(templateId, false, false);
    m_playheadUs = playhead;
    if (newClipId.isEmpty()) {
        m_project = before;
        if (m_assetLibrary)
            m_assetLibrary->syncToProject();
        return {};
    }

    // Back on the old one's track when there is room there, so the stack keeps its order.
    int nt = -1;
    int nc = -1;
    drift::mcpdetail::findClipById(m_project, newClipId, &nt, &nc);
    const int ot = m_project.trackIndexById(oldTrackId);
    if (nt >= 0 && ot >= 0 && ot != nt) {
        const drift::Clip placed = m_project.tracks().at(nt).clips.at(nc);
        const drift::Track &target = m_project.tracks().at(ot);
        bool room = target.allowsClipType(placed.type) && !target.isAdjustment();
        for (const drift::Clip &other : target.clips)
            room = room && (other.timelineEnd() <= placed.timelineStart || other.timelineStart >= placed.timelineEnd());
        if (room) {
            m_project.tracks()[nt].clips.removeAt(nc);
            const bool emptied = m_project.tracks().at(nt).clips.isEmpty();
            drift::Track &dest = m_project.tracks()[ot];
            int at = 0;
            while (at < dest.clips.size() && dest.clips.at(at).timelineStart < placed.timelineStart)
                ++at;
            dest.clips.insert(at, placed);
            if (emptied)
                m_project.tracks().removeAt(nt);
        }
    }
    // Effect or mask lanes the user pinned to the old one follow the new one.
    m_project.forEachTrackList([&](QList<drift::Track> &tracks) {
        for (drift::Track &track : tracks) {
            for (drift::Clip &clip : track.clips) {
                if (clip.linkedClipId == oldClip.id)
                    clip.linkedClipId = newClipId;
            }
        }
    });

    // Refill: pictures in slot order, texts by what they are for (then by position).
    const drift::Clip *placedClip = findClipAnywhere(m_project, newClipId);
    const QString newAssetId = placedClip ? placedClip->assetId : QString();
    const QVariantMap newInfo = sceneTemplateInfo(newAssetId);
    const QVariantList newSlots = newInfo.value(QStringLiteral("slots")).toList();
    const int fills = int(qMin(pictures.size(), newSlots.size()));
    for (int i = 0; i < fills; ++i)
        fillTemplateSlotWithAsset(newSlots.at(i).toMap().value(QStringLiteral("clipId")).toString(), pictures.at(i),
                                  false);
    const QVariantList newTexts = newInfo.value(QStringLiteral("texts")).toList();
    QSet<int> taken;
    int carriedTexts = 0;
    for (int i = 0; i < oldTexts.size(); ++i) {
        const QVariantMap old = oldTexts.at(i).toMap();
        if (!old.value(QStringLiteral("edited")).toBool())
            continue;
        int pick = -1;
        for (int j = 0; j < newTexts.size() && pick < 0; ++j) {
            if (!taken.contains(j)
                && newTexts.at(j).toMap().value(QStringLiteral("kind")) == old.value(QStringLiteral("kind")))
                pick = j;
        }
        if (pick < 0 && i < newTexts.size() && !taken.contains(i))
            pick = i;
        if (pick < 0)
            continue;
        taken.insert(pick);
        if (drift::Clip *clip = findClipAnywhere(m_project, newTexts.at(pick).toMap().value(QStringLiteral("clipId")).toString())) {
            clip->textContent = old.value(QStringLiteral("text")).toString();
            ++carriedTexts;
        }
    }

    // The old composition goes when nothing shows it any more, with the stand-ins and music of its folder.
    bool used = false;
    m_project.forEachTrackList([&](const QList<drift::Track> &tracks) {
        for (const drift::Track &track : tracks) {
            for (const drift::Clip &clip : track.clips)
                used = used || clip.assetId == compositeAssetId;
        }
    });
    if (!used) {
        m_project.assets().remove(compositeAssetId);
        m_project.assetOrder().removeAll(compositeAssetId);
        pruneOrphanSequences();
        if (!oldFolderId.isEmpty()) {
            QSet<QString> inUse;
            m_project.forEachTrackList([&](const QList<drift::Track> &tracks) {
                for (const drift::Track &track : tracks) {
                    for (const drift::Clip &clip : track.clips)
                        inUse.insert(clip.assetId);
                }
            });
            bool folderEmpty = true;
            for (const QString &id : QStringList(m_project.assetOrder())) {
                const drift::MediaAsset *asset = m_project.asset(id);
                if (!asset || asset->folderId != oldFolderId)
                    continue;
                if (inUse.contains(id)) {
                    folderEmpty = false;
                    continue;
                }
                m_project.assets().remove(id);
                m_project.assetOrder().removeAll(id);
            }
            bool hasChildren = false;
            for (const drift::BinFolder &folder : m_project.binFolders())
                hasChildren = hasChildren || folder.parentId == oldFolderId;
            if (folderEmpty && !hasChildren) {
                m_project.binFolders().remove(oldFolderId);
                m_project.binFolderOrder().removeAll(oldFolderId);
            }
        }
    }
    if (m_assetLibrary)
        m_assetLibrary->syncToProject();
    pushProjectEdit(before, tr("Change template"));
    finishEdit(QString());
    selectClipById(newClipId);
    emit sequenceTabsChanged();
    const int lost = int(pictures.size()) - fills;
    QString message = tr("Template changed: %n photo(s) carried over", "", fills);
    if (carriedTexts > 0)
        message += QStringLiteral(", ") + tr("%n text(s)", "", carriedTexts);
    if (lost > 0)
        message += QStringLiteral(". ") + tr("%n photo(s) did not fit in the new one", "", lost);
    setLastMessage(message, lost > 0 ? QStringLiteral("warning") : QStringLiteral("info"));
    return newClipId;
}

// --- Text form --------------------------------------------------------------------------------

int AppController::setTemplateTexts(const QVariantMap &textsByClipId)
{
    int changes = 0;
    for (auto it = textsByClipId.cbegin(); it != textsByClipId.cend(); ++it) {
        const drift::Clip *clip = findClipAnywhere(m_project, it.key());
        changes += clip && !clip->placeholderId.isEmpty() && clip->textContent != it.value().toString() ? 1 : 0;
    }
    if (changes == 0)
        return 0;
    const drift::Project before = m_project.detachedCopy();
    for (auto it = textsByClipId.cbegin(); it != textsByClipId.cend(); ++it) {
        drift::Clip *clip = findClipAnywhere(m_project, it.key());
        if (clip && !clip->placeholderId.isEmpty())
            clip->textContent = it.value().toString();
    }
    pushProjectEdit(before, tr("Template texts"));
    finishEdit(QString());
    setLastMessage(tr("%n text(s) changed", "", changes), QStringLiteral("info"));
    return changes;
}

// --- Cuts to the beat ---------------------------------------------------------------------------

void AppController::fitTemplateCutsToBeat(const QString &compositeAssetId)
{
    const drift::MediaAsset *asset = m_project.asset(compositeAssetId);
    if (!asset || sceneGenerator(*asset).isEmpty() || m_templateBeatFitRunning)
        return;
    const QString sequenceId = asset->sequenceId;
    bool ownMusic = false;
    for (const drift::Track &track : m_project.sequenceTracks(sequenceId)) {
        if (track.type == drift::TrackType::Audio && !track.muted)
            ownMusic = ownMusic || !track.clips.isEmpty();
    }
    // Its own music when it has some; else whatever plays under it on the main timeline.
    drift::Project snap;
    drift::TimeUs startUs = 0;
    drift::TimeUs durUs = m_project.sequenceDurationUs(sequenceId);
    drift::TimeUs offsetUs = 0; // analysis time - offset = time inside the composition
    if (ownMusic) {
        snap = m_project.sequenceView(sequenceId);
    } else {
        const drift::Clip *instance = nullptr;
        for (const drift::Track &track : m_project.rootTracks()) {
            for (const drift::Clip &clip : track.clips) {
                if (!instance && clip.assetId == compositeAssetId)
                    instance = &clip;
            }
        }
        if (!instance) {
            setLastMessage(tr("The template has no music: change its music first"), QStringLiteral("warning"));
            return;
        }
        snap = m_project.sequenceView(QString());
        startUs = instance->timelineStart;
        durUs = instance->timelineDuration;
        offsetUs = instance->timelineStart - instance->srcIn;
    }
    if (durUs <= 0)
        return;
    m_templateBeatFitRunning = true;
    emit templateBeatFitChanged();
    setLastMessage(tr("Listening to the music to find its beat…"), QStringLiteral("info"));
    const quint64 generation = ++m_templateBeatFitGeneration;
    (void)QtConcurrent::run([this, snap, startUs, durUs, offsetUs, generation, compositeAssetId] {
        const AudioBeatAnalysis analysis =
            drift::mcpdetail::runBeatAnalysis(snap, startUs, durUs, drift::usToSeconds(startUs));
        QMetaObject::invokeMethod(
            this,
            [this, analysis, offsetUs, generation, compositeAssetId] {
                if (generation != m_templateBeatFitGeneration)
                    return;
                m_templateBeatFitRunning = false;
                emit templateBeatFitChanged();
                applyTemplateBeatFit(compositeAssetId, analysis, offsetUs);
            },
            Qt::QueuedConnection);
    });
}

void AppController::applyTemplateBeatFit(const QString &compositeAssetId, const AudioBeatAnalysis &analysis,
                                         drift::TimeUs offsetUs)
{
    const drift::MediaAsset *asset = m_project.asset(compositeAssetId);
    if (!asset)
        return;
    const QString sequenceId = asset->sequenceId;
    const drift::TimeUs lengthUs = m_project.sequenceDurationUs(sequenceId);
    QList<drift::TimeUs> beats;
    for (const double b : analysis.beats)
        beats.append(drift::secondsToUs(b) - offsetUs);
    if (beats.size() < 2) {
        // No steady tempo: the strong hits will do.
        for (const AudioOnset &onset : analysis.onsets) {
            if (onset.strength >= 0.35f)
                beats.append(drift::secondsToUs(onset.seconds) - offsetUs);
        }
        std::sort(beats.begin(), beats.end());
    }
    const bool steady = beats.size() < 2;
    if (steady)
        beats = drift::steadyBeatGrid(0, lengthUs); // silence: the 120 BPM the effect templates use

    QList<drift::Track> *tracks = writableSequenceTracks(m_project, sequenceId);
    if (!tracks)
        return;
    const drift::Project before = m_project.detachedCopy();
    tracks = writableSequenceTracks(m_project, sequenceId);
    const int moved = drift::retimeTemplateSlotsToBeats(
        *tracks, beats, drift::secondsToUs(0.4), [this](const QString &assetId) -> drift::TimeUs {
            const drift::MediaAsset *media = m_project.asset(assetId);
            return media ? media->durationUs : 0;
        });
    if (moved == 0) {
        setLastMessage(tr("The cuts already fall on the beat"), QStringLiteral("info"));
        return;
    }
    pushProjectEdit(before, tr("Fit cuts to the beat"));
    finishEdit(QString());
    setLastMessage(steady ? tr("No beat found in the music: %n cut(s) now follow a steady 120 BPM beat", "", moved)
                          : tr("%n cut(s) moved to the beat of the music", "", moved),
                   QStringLiteral("info"));
}

void AppController::replaceTemplateMusic(const QString &compositeAssetId, const QUrl &url, bool fitCuts)
{
    const QString path = url.isLocalFile() ? url.toLocalFile() : url.toString();
    if (!m_assetLibrary || !m_project.asset(compositeAssetId))
        return;
    if (!AssetLibrary::isAudioPath(path) && !AssetLibrary::isVideoPath(path)) {
        setLastMessage(tr("Choose a song or an audio file"), QStringLiteral("warning"));
        return;
    }
    const QStringList ids = m_assetLibrary->importLocalPaths({path});
    if (ids.isEmpty())
        return;
    const QString musicId = ids.first();
    const auto apply = [this, compositeAssetId, musicId, fitCuts] {
        if (setTemplateMusicAsset(compositeAssetId, musicId) && fitCuts)
            fitTemplateCutsToBeat(compositeAssetId);
    };
    if (!m_assetLibrary->isImportPending(musicId)) {
        apply();
        return;
    }
    auto connection = std::make_shared<QMetaObject::Connection>();
    *connection = connect(m_assetLibrary, &AssetLibrary::assetMetadataChanged, this,
                          [this, musicId, apply, connection](const QString &assetId) {
                              if (assetId != musicId || m_assetLibrary->isImportPending(assetId))
                                  return;
                              disconnect(*connection);
                              apply();
                          });
}

bool AppController::setTemplateMusicAsset(const QString &compositeAssetId, const QString &musicAssetId)
{
    const drift::MediaAsset *asset = m_project.asset(compositeAssetId);
    const drift::MediaAsset *music = m_project.asset(musicAssetId);
    if (!asset || !music || music->durationUs <= 0 || !(music->kind == drift::MediaKind::Audio || music->hasAudio)) {
        setLastMessage(tr("That file has no sound to use as music"), QStringLiteral("warning"));
        return false;
    }
    const QString sequenceId = asset->sequenceId;
    const drift::TimeUs lengthUs = m_project.sequenceDurationUs(sequenceId);
    const drift::Project before = m_project.detachedCopy();
    QList<drift::Track> *tracks = writableSequenceTracks(m_project, sequenceId);
    if (!tracks || lengthUs <= 0)
        return false;
    music = m_project.asset(musicAssetId);

    int audioTrack = -1;
    for (int t = 0; t < tracks->size(); ++t) {
        drift::Track &track = (*tracks)[t];
        if (track.type != drift::TrackType::Audio)
            continue;
        if (audioTrack < 0)
            audioTrack = t;
        track.clips.clear();
        track.transitions.clear();
    }
    if (audioTrack < 0) {
        drift::Track track;
        track.id = QUuid::createUuid().toString(QUuid::WithoutBraces);
        track.type = drift::TrackType::Audio;
        track.name = tr("Music");
        tracks->append(track);
        audioTrack = int(tracks->size()) - 1;
    }
    drift::Clip clip;
    clip.id = QUuid::createUuid().toString(QUuid::WithoutBraces);
    clip.type = drift::ClipType::Audio;
    clip.assetId = music->id;
    clip.path = music->path;
    clip.name = music->name;
    clip.timelineStart = 0;
    clip.timelineDuration = qMin(lengthUs, music->durationUs);
    clip.srcIn = 0;
    clip.srcOut = clip.timelineDuration;
    clip.fadeOutUs = qMin<drift::TimeUs>(500'000, clip.timelineDuration / 4);
    (*tracks)[audioTrack].clips.append(clip);
    // The music plays instead of the videos' own sound, as when a template comes with music.
    for (drift::Track &track : *tracks) {
        for (drift::Clip &other : track.clips) {
            if (other.type == drift::ClipType::Video)
                other.suppressEmbeddedAudio = true;
        }
    }
    pushProjectEdit(before, tr("Template music"));
    finishEdit(QString());
    setLastMessage(tr("New music: %1").arg(music->name), QStringLiteral("info"));
    return true;
}

// --- My brand ---------------------------------------------------------------------------------

drift::BrandKit AppController::currentBrandKit() const
{
    QSettings settings;
    settings.beginGroup(kBrandGroup);
    drift::BrandKit kit;
    kit.logoPath = settings.value(QStringLiteral("logo")).toString();
    if (!kit.logoPath.isEmpty() && !QFileInfo::exists(kit.logoPath))
        kit.logoPath.clear();
    for (const QString &name : settings.value(QStringLiteral("colors")).toStringList()) {
        const QColor color(name);
        if (color.isValid())
            kit.colors.append(color);
    }
    kit.fontFamily = settings.value(QStringLiteral("font")).toString();
    return kit;
}

bool AppController::brandKitAutoApply() const
{
    QSettings settings;
    return settings.value(QStringLiteral("brandKit/autoApply"), true).toBool();
}

bool AppController::templateWantsBrand(const QString &category, const QStringList &tags,
                                       const QList<drift::Track> &tracks)
{
    if (category == QLatin1String("business") || tags.contains(QStringLiteral("logo"), Qt::CaseInsensitive)
        || tags.contains(QStringLiteral("brand"), Qt::CaseInsensitive))
        return true;
    for (const drift::Track &track : tracks) {
        for (const drift::Clip &clip : track.clips) {
            if (!clip.brandRole.isEmpty() || clip.placeholderLabel.contains(QLatin1String("logo"), Qt::CaseInsensitive))
                return true;
        }
    }
    return false;
}

QVariantMap AppController::brandKit() const
{
    const drift::BrandKit kit = currentBrandKit();
    QStringList colors;
    for (const QColor &color : kit.colors)
        colors.append(color.name(QColor::HexRgb));
    return QVariantMap{
        {QStringLiteral("logo"), kit.logoPath.isEmpty() ? QString() : QUrl::fromLocalFile(kit.logoPath).toString()},
        {QStringLiteral("logoPath"), kit.logoPath},
        {QStringLiteral("colors"), colors},
        {QStringLiteral("font"), kit.fontFamily},
        {QStringLiteral("autoApply"), brandKitAutoApply()},
        {QStringLiteral("empty"), kit.isEmpty()},
    };
}

bool AppController::setBrandKit(const QVariantMap &values)
{
    QSettings settings;
    settings.beginGroup(kBrandGroup);
    // The logo is copied in, so the kit survives the original being moved or deleted.
    const QString logoUrl = values.value(QStringLiteral("logo")).toString();
    QString logo = logoUrl.startsWith(QLatin1String("file:")) ? QUrl(logoUrl).toLocalFile() : logoUrl;
    const QString dir = QDir(QStandardPaths::writableLocation(QStandardPaths::AppDataLocation)).filePath(QStringLiteral("brand"));
    if (!logo.isEmpty() && QDir::cleanPath(QFileInfo(logo).absolutePath()) != QDir::cleanPath(dir)) {
        if (!AssetLibrary::isImagePath(logo) || QImageReader(logo).size().isEmpty()) {
            setLastMessage(tr("The logo has to be a picture (PNG, JPG, WebP…)"), QStringLiteral("warning"));
            return false;
        }
        QDir().mkpath(dir);
        const QString target = QDir(dir).filePath(
            QStringLiteral("logo-%1.%2").arg(QDateTime::currentMSecsSinceEpoch()).arg(QFileInfo(logo).suffix().toLower()));
        if (!QFile::copy(logo, target)) {
            setLastMessage(tr("Could not copy the logo"), QStringLiteral("error"));
            return false;
        }
        const QString old = settings.value(QStringLiteral("logo")).toString();
        if (!old.isEmpty() && QDir::cleanPath(QFileInfo(old).absolutePath()) == QDir::cleanPath(dir))
            QFile::remove(old);
        logo = target;
    } else if (logo.isEmpty()) {
        const QString old = settings.value(QStringLiteral("logo")).toString();
        if (!old.isEmpty() && QDir::cleanPath(QFileInfo(old).absolutePath()) == QDir::cleanPath(dir))
            QFile::remove(old);
    }
    QStringList colors;
    for (const QVariant &value : values.value(QStringLiteral("colors")).toList()) {
        const QColor color(value.toString());
        if (color.isValid() && colors.size() < 4)
            colors.append(color.name(QColor::HexRgb));
    }
    settings.setValue(QStringLiteral("logo"), logo);
    settings.setValue(QStringLiteral("colors"), colors);
    settings.setValue(QStringLiteral("font"), values.value(QStringLiteral("font")).toString().trimmed());
    settings.setValue(QStringLiteral("autoApply"), values.value(QStringLiteral("autoApply"), true).toBool());
    settings.endGroup();
    emit brandKitChanged();
    setLastMessage(tr("My brand saved"), QStringLiteral("info"));
    return true;
}

bool AppController::applyBrandKitToTemplate(const QString &compositeAssetId)
{
    const drift::MediaAsset *asset = m_project.asset(compositeAssetId);
    const drift::BrandKit kit = currentBrandKit();
    if (!asset || sceneGenerator(*asset).isEmpty())
        return false;
    if (kit.isEmpty()) {
        setLastMessage(tr("Set up My brand first (Templates › My brand)"), QStringLiteral("warning"));
        return false;
    }
    const QString sequenceId = asset->sequenceId;
    const drift::Project before = m_project.detachedCopy();
    QList<drift::Track> *tracks = writableSequenceTracks(m_project, sequenceId);
    if (!tracks)
        return false;
    const drift::BrandApplyResult result = drift::applyBrandKit(*tracks, kit);
    const int logos = fillLogoSlots(sequenceId, result.logoSlots);
    if (result.recoloured + result.refonted + logos == 0) {
        setLastMessage(tr("This template has no logo slot or brand texts to change"), QStringLiteral("info"));
        return false;
    }
    if (m_assetLibrary)
        m_assetLibrary->syncToProject();
    pushProjectEdit(before, tr("Apply my brand"));
    finishEdit(QString());
    setLastMessage(tr("My brand applied"), QStringLiteral("info"));
    return true;
}

int AppController::fillLogoSlots(const QString &sequenceId, const QStringList &placeholderIds)
{
    const drift::BrandKit kit = currentBrandKit();
    if (placeholderIds.isEmpty() || kit.logoPath.isEmpty() || !m_assetLibrary)
        return 0;
    // One asset for the logo per project.
    QString logoId;
    for (const drift::MediaAsset &asset : m_project.assets()) {
        if (asset.kind == drift::MediaKind::Image && QFileInfo(asset.path) == QFileInfo(kit.logoPath))
            logoId = asset.id;
    }
    if (logoId.isEmpty()) {
        QImageReader reader(kit.logoPath);
        reader.setAutoTransform(true);
        QSize size = reader.size();
        if (reader.transformation() & QImageIOHandler::TransformationRotate90)
            size.transpose();
        if (size.isEmpty())
            return 0;
        drift::MediaAsset logo;
        logo.kind = drift::MediaKind::Image;
        logo.name = tr("My logo");
        logo.path = kit.logoPath;
        logo.thumbnailPath = kit.logoPath;
        logo.width = size.width();
        logo.height = size.height();
        logoId = m_assetLibrary->addGeneratedAsset(logo);
    }
    if (logoId.isEmpty())
        return 0;
    int filled = 0;
    for (const QString &placeholderId : placeholderIds) {
        QString clipId;
        for (const drift::Track &track : m_project.sequenceTracks(sequenceId)) {
            for (const drift::Clip &clip : track.clips) {
                if (clipId.isEmpty() && clip.placeholderId == placeholderId && !isTextKind(clip.type))
                    clipId = clip.id;
            }
        }
        if (!clipId.isEmpty() && fillTemplateSlotWithAsset(clipId, logoId, false, true))
            ++filled;
    }
    return filled;
}
