#pragma once

#include <QList>
#include <QString>
#include <QStringList>

namespace drift::spell {

// A word the system spell checker flags in one of the texts given to check().
struct Issue
{
    int text = -1;   // index into the texts
    int start = 0;   // UTF-16 offset of the word in that text
    int length = 0;
    QString word;
    QStringList suggestions; // best first; empty when the checker has none
};

// The operating system's spell checker (Windows' ISpellChecker; elsewhere none yet). language is
// a code like "es", "es_CO" or "pt-BR": the closest installed dictionary of that language is used.
bool available(const QString &language);
QList<Issue> check(const QStringList &texts, const QString &language, int maxSuggestions = 4);

} // namespace drift::spell
