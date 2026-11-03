#pragma once

#include <QString>
#include <QStringList>

#include <memory>

namespace drift {

// Translation on the computer (0.30, Jorge): M2M100 418M (MIT, int8 ONNX, 100 languages), for the
// captions when DeepL on our server cannot answer: no account, no internet, or the month's quota
// spent. Slower and a little rougher than DeepL, and it needs no one.
//
// The model comes as an addon of kind "translate-model" (or DRIFT_TRANSLATE_MODEL_DIR):
// encoder.onnx, decoder.onnx (without the KV cache: a caption is short, so the decoder simply runs
// on the whole sequence each step), vocab.txt (one piece a line, id = line, the language tokens
// included) and merges.txt (one "a b" a line, rank = line), converted from the model's
// tokenizer.json. Tokenizing is NFKC, a split on whitespace, "▁" before each word and BPE by rank
// (consecutive unknowns collapse); the source is [__src__] pieces </s>, the decoder starts with
// </s> __tgt__ and decodes greedily: checked against the reference in flip-addons/work.
class TextTranslator
{
    struct Impl;

public:
    static bool modelPresent();

    // The model's code for a language the app names (DeepL's "pt-BR", "zh"…), or empty when it has
    // none.
    static QString languageCode(const QString &appCode);

    // Loads (or reuses) the model. nullptr with *error set when unusable. Blocks.
    static std::shared_ptr<TextTranslator> load(QString *error);

    // Each text from `source` (a language code, or empty: Spanish is assumed then) into `target`;
    // empty with *error set on failure. Blocks; one at a time.
    QStringList translate(const QStringList &texts, const QString &source, const QString &target, QString *error);

    ~TextTranslator();
    TextTranslator(const TextTranslator &) = delete;
    TextTranslator &operator=(const TextTranslator &) = delete;

private:
    TextTranslator();
    std::unique_ptr<Impl> d;
};

} // namespace drift
