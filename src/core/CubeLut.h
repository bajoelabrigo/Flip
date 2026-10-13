#pragma once

#include <QImage>
#include <QString>
#include <QStringList>
#include <QVector>

namespace drift {

// A colour look-up table read from an Adobe/Resolve .cube file.
//
// Supported, and checked on load:
// - 3D tables (LUT_3D_SIZE) from 2 to kMaxCube3dSize points per side, and 1D tables (LUT_1D_SIZE)
//   from 2 to kMaxCube1dSize entries; one table per file.
// - TITLE "…", DOMAIN_MIN r g b and DOMAIN_MAX r g b (each max above its min; default 0 and 1).
// - '#' comments, blank lines, tabs, CRLF, and LUT_3D_INPUT_RANGE / LUT_1D_INPUT_RANGE lo hi
//   (Resolve's spelling of the same domain).
// - Numbers always with a '.' decimal point, whatever the system's locale, as the format says.
// - Table rows are "r g b", red changing fastest, then green, then blue (the standard order).
// Files larger than kMaxCubeFileBytes are refused before reading.
//
// Values are kept as read (they may go past 0..1, as some technical LUTs do); applying clamps.
struct CubeLut
{
    static constexpr int kMaxCube3dSize = 129;
    static constexpr int kMaxCube1dSize = 65536;
    static constexpr qint64 kMaxCubeFileBytes = 64ll * 1024 * 1024;

    QString title;
    bool is3d = true;
    int size = 0; // points per side (3D) or entries (1D)
    float domainMin[3] = {0.f, 0.f, 0.f};
    float domainMax[3] = {1.f, 1.f, 1.f};
    QVector<float> rgb; // size^3 (3D) or size (1D) triplets, in file order

    bool isValid() const { return size >= 2 && rgb.size() == entryCount() * 3; }
    int entryCount() const { return is3d ? size * size * size : size; }

    // Parses .cube text. On failure returns an invalid table and sets *error to a sentence the
    // person can act on (translated, context "CubeLut").
    static CubeLut parse(const QByteArray &text, QString *error = nullptr);
    static CubeLut load(const QString &path, QString *error = nullptr);

    // The table as a 16-bit texture for the GPU: a 3D table becomes size slices of size x size
    // laid side by side (width size*size, height size; slice b holds blue = b, red along x, green
    // along y); a 1D table is one row of size texels. Alpha is opaque.
    QImage toTexture() const;

    // The colour this table gives for an RGB input (0..1, domain applied), trilinear for 3D and
    // linear for 1D. What the shader does, on the CPU: for thumbnails and tests.
    void lookup(const float in[3], float out[3]) const;
    // A picture through the table, mixed with the original by intensity (0..1). Alpha is kept.
    QImage apply(const QImage &image, double intensity = 1.0) const;

    // Where a LUT a project names can be found when it is not at its saved path any more (the
    // project moved to another folder or computer): the same file name in each of these folders,
    // in order. The app sets them: the person's LUT library, the factory LUTs, and the open
    // project's folder (and its "luts" subfolder).
    static void setSearchDirs(const QStringList &dirs);
    static QStringList searchDirs();
    // path itself when it exists, else the first same-named file in the search folders, else "".
    static QString resolve(const QString &path);
};

} // namespace drift
