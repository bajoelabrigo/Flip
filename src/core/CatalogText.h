#pragma once

#include <QCoreApplication>
#include <QString>

namespace drift {

// A name read from a bundled catalog's JSON (an effect, a transition, one of their parameters, a
// text animation), in the interface language. tools/i18n/catalog_strings.py lists every such name
// for lupdate under the "Catalog" context; a name it does not know — a user's own package — comes
// back as written.
inline QString catalogText(const QString &text)
{
    if (text.isEmpty())
        return text;
    return QCoreApplication::translate("Catalog", text.toUtf8().constData());
}

} // namespace drift
