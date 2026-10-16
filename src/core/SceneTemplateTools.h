#pragma once

#include "core/Clip.h"
#include "core/Time.h"
#include "core/Track.h"

#include <QColor>
#include <QList>
#include <QString>
#include <QStringList>

#include <functional>

// Helpers behind the "faster use" of scene templates (0.14.0): suggesting templates for a set of
// photos, re-timing a template's cuts to the music, naming the fields of its texts and applying a
// brand kit. Pure functions over tracks and numbers, so the rules can be tested without the app.
namespace drift {

// --- Use with my photos ---------------------------------------------------------------------

// "vertical" | "horizontal" | "square" for a w×h picture or canvas (square within 8 %).
QString shapeOfSize(int width, int height);
// The shape most of the pictures have; ties go vertical, then square, then horizontal (phones).
QString majorityShape(int vertical, int horizontal, int square);
// The Stock "photos" filter bucket a count falls in: "0" | "1" | "2-3" | "4-6" | "7+".
QString photoCountBucket(int count);
// The bucket after `bucket` (more photos), or empty after "7+".
QString nextPhotoCountBucket(const QString &bucket);

// How well a template fits mediaCount pictures of shape `mediaShape` in a project of
// projectShape (empty when the project is empty and takes the template's shape). Higher is
// better; below 0 it is not worth suggesting (no slots at all).
double sceneTemplateMatchScore(int slotCount, const QString &templateShape, int mediaCount, const QString &mediaShape,
                               const QString &projectShape);

// --- Fit the cuts to the beat ---------------------------------------------------------------

// A steady grid of beats in [startUs, endUs) at `bpm`, from startUs.
QList<TimeUs> steadyBeatGrid(TimeUs startUs, TimeUs endUs, double bpm = 120.0);

// Moves each cut (sorted) to the nearest beat, keeping their order, at least minGapUs between two
// cuts and between a cut and the bounds. A cut with no beat in its allowed window stays where it
// was (clamped into the window).
QList<TimeUs> snapCutsToBeats(const QList<TimeUs> &cuts, const QList<TimeUs> &beats, TimeUs startUs, TimeUs endUs,
                              TimeUs minGapUs);

// Re-times the cuts between a template's consecutive photo/video slots (clips with a placeholderId
// on the same track, end to end or overlapping by a transition) to the beats, times in the tracks'
// own clock. The first slot's start and the last slot's end stay put; an overlap (transition)
// keeps its width; lanes linked to a moved slot follow it. `mediaDurationUs` gives a video slot's
// source length (0 = unknown). Returns how many cuts moved.
int retimeTemplateSlotsToBeats(QList<Track> &tracks, const QList<TimeUs> &beats, TimeUs minDurationUs,
                               const std::function<TimeUs(const QString &assetId)> &mediaDurationUs = {});

// --- Text form --------------------------------------------------------------------------------

// What a template text is for, guessed from what it says (and the label its author gave it):
// "business", "phone", "price", "discount", "date", "time", "web", "email", "handle", "address",
// "cta", "title", "subtitle" or "text".
QString guessTemplateTextKind(const QString &text, const QString &label = QString(), bool largest = false);

// --- Brand kit --------------------------------------------------------------------------------

struct BrandKit
{
    QString logoPath;
    QList<QColor> colors; // primary, secondary, accent, text (2 to 4 of them)
    QString fontFamily;

    bool isEmpty() const { return logoPath.isEmpty() && colors.isEmpty() && fontFamily.isEmpty(); }
    // The colour of a brand role, falling back to the primary one; invalid when there is none.
    QColor colorFor(const QString &role) const;
};

struct BrandApplyResult
{
    QStringList logoSlots; // placeholderIds of the slots that take the logo
    int recoloured = 0;
    int refonted = 0;
};

// Applies the kit to a template's tracks before they go in. Clips marked with brandRole follow it
// (FORMAT.md); a template without marks still gets the logo in a slot whose label says "logo" and
// the font on its title texts (the largest editable texts).
BrandApplyResult applyBrandKit(QList<Track> &tracks, const BrandKit &kit);

} // namespace drift
