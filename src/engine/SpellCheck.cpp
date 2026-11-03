#include "SpellCheck.h"

#ifdef Q_OS_WIN
#include <windows.h>
#include <objbase.h>
#include <spellcheck.h>
#endif

namespace drift::spell {

#ifdef Q_OS_WIN
namespace {

template <class T>
struct ComRef
{
    T *p = nullptr;
    ComRef() = default;
    ComRef(const ComRef &) = delete;
    ComRef &operator=(const ComRef &) = delete;
    ~ComRef()
    {
        if (p)
            p->Release();
    }
    T **put() { return &p; }
    T *operator->() const { return p; }
    explicit operator bool() const { return p != nullptr; }
};

// The GUI thread already runs COM (Qt's OLE); this only balances a call made from elsewhere.
struct ComScope
{
    HRESULT hr = CoInitializeEx(nullptr, COINIT_APARTMENTTHREADED);
    ~ComScope()
    {
        if (SUCCEEDED(hr))
            CoUninitialize();
    }
};

LPCWSTR wide(const QString &s)
{
    return reinterpret_cast<LPCWSTR>(s.utf16());
}

// The installed dictionary closest to `language`: the exact tag, else the first of that language.
QString pickTag(ISpellCheckerFactory *factory, const QString &language)
{
    QString want = language.trimmed();
    want.replace(QLatin1Char('_'), QLatin1Char('-'));
    const auto supported = [factory](const QString &tag) {
        BOOL ok = FALSE;
        return SUCCEEDED(factory->IsSupported(wide(tag), &ok)) && ok;
    };
    if (!want.isEmpty() && supported(want))
        return want;
    const QString base = want.section(QLatin1Char('-'), 0, 0).toLower();
    if (base.isEmpty())
        return {};
    ComRef<IEnumString> list;
    if (FAILED(factory->get_SupportedLanguages(list.put())) || !list)
        return {};
    QString found;
    LPOLESTR tag = nullptr;
    while (list->Next(1, &tag, nullptr) == S_OK) {
        const QString t = QString::fromWCharArray(tag);
        CoTaskMemFree(tag);
        if (found.isEmpty() && t.section(QLatin1Char('-'), 0, 0).toLower() == base)
            found = t;
    }
    return found;
}

bool makeChecker(const QString &language, ComRef<ISpellChecker> &checker)
{
    ComRef<ISpellCheckerFactory> factory;
    if (FAILED(CoCreateInstance(__uuidof(SpellCheckerFactory), nullptr, CLSCTX_INPROC_SERVER,
                                IID_PPV_ARGS(factory.put())))
        || !factory)
        return false;
    const QString tag = pickTag(factory.p, language);
    if (tag.isEmpty())
        return false;
    return SUCCEEDED(factory->CreateSpellChecker(wide(tag), checker.put())) && checker;
}

} // namespace

bool available(const QString &language)
{
    ComScope com;
    ComRef<ISpellChecker> checker;
    return makeChecker(language, checker);
}

QList<Issue> check(const QStringList &texts, const QString &language, int maxSuggestions)
{
    QList<Issue> issues;
    ComScope com;
    ComRef<ISpellChecker> checker;
    if (!makeChecker(language, checker))
        return issues;
    for (int i = 0; i < texts.size(); ++i) {
        const QString &text = texts.at(i);
        ComRef<IEnumSpellingError> errors;
        if (FAILED(checker->Check(wide(text), errors.put())) || !errors)
            continue;
        for (;;) {
            ComRef<ISpellingError> error;
            if (errors->Next(error.put()) != S_OK || !error)
                break;
            ULONG start = 0;
            ULONG length = 0;
            CORRECTIVE_ACTION action = CORRECTIVE_ACTION_NONE;
            error->get_StartIndex(&start);
            error->get_Length(&length);
            error->get_CorrectiveAction(&action);
            if (length == 0 || int(start + length) > text.size())
                continue;
            Issue issue;
            issue.text = i;
            issue.start = int(start);
            issue.length = int(length);
            issue.word = text.mid(issue.start, issue.length);
            if (issue.word.contains(QLatin1Char('*'))) // a masked swear word, on purpose
                continue;
            if (action == CORRECTIVE_ACTION_REPLACE) {
                LPWSTR replacement = nullptr;
                if (SUCCEEDED(error->get_Replacement(&replacement)) && replacement) {
                    issue.suggestions.append(QString::fromWCharArray(replacement));
                    CoTaskMemFree(replacement);
                }
            } else if (action == CORRECTIVE_ACTION_DELETE) {
                issue.suggestions.append(QString()); // a repeated word: removing it is the fix
            } else if (action == CORRECTIVE_ACTION_GET_SUGGESTIONS) {
                ComRef<IEnumString> suggestions;
                if (SUCCEEDED(checker->Suggest(wide(issue.word), suggestions.put())) && suggestions) {
                    LPOLESTR s = nullptr;
                    while (issue.suggestions.size() < maxSuggestions && suggestions->Next(1, &s, nullptr) == S_OK) {
                        issue.suggestions.append(QString::fromWCharArray(s));
                        CoTaskMemFree(s);
                    }
                }
            }
            issues.append(issue);
        }
    }
    return issues;
}

#else

bool available(const QString &)
{
    return false;
}

QList<Issue> check(const QStringList &, const QString &, int)
{
    return {};
}

#endif

} // namespace drift::spell
