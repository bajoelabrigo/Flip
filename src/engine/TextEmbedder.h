#pragma once

#include <QString>

#include <memory>
#include <vector>

namespace drift {

// Sentence embeddings with paraphrase-multilingual-MiniLM-L12-v2 (Apache-2.0, int8 ONNX) for the
// simple "AI text": the idea someone types, in any of its 50+ languages, is matched to the closest
// of the app's text styles by cosine similarity.
//
// The model comes as an addon of kind "text-embed-model" (or DRIFT_TEXTEMBED_MODEL_DIR): model.onnx
// and vocab.txt, the XLM-R SentencePiece Unigram vocabulary as one "piece<TAB>score" a line (id =
// line number), converted from the model's tokenizer.json. Tokenizing is NFKC, a split on
// whitespace, "▁" before each word and the best-scoring segmentation of each (consecutive unknowns
// collapse), between <s> (0) and </s> (2): checked identical to the Hugging Face tokenizer.
class TextEmbedder
{
    struct Impl;

public:
    static bool modelPresent();

    // Loads (or reuses) the model and vocabulary. nullptr with *error set when unusable. Blocks.
    static std::shared_ptr<TextEmbedder> load(QString *error);

    // Mean-pooled, L2-normalised embedding (384 floats); empty with *error set on failure.
    std::vector<float> embed(const QString &text, QString *error);

    static float cosine(const std::vector<float> &a, const std::vector<float> &b);

    ~TextEmbedder();
    TextEmbedder(const TextEmbedder &) = delete;
    TextEmbedder &operator=(const TextEmbedder &) = delete;

private:
    TextEmbedder();
    std::unique_ptr<Impl> d;
};

} // namespace drift
