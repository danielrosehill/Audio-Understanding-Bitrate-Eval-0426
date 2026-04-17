# Methodology

## Scope

Measure the effect of MP3 bitrate on transcription accuracy when audio is sent to multimodal LLMs via OpenRouter's OpenAI-compatible `chat/completions` endpoint with `input_audio` content parts.

## Models covered

Every model in OpenRouter's catalog as of April 2026 whose `architecture.input_modalities` includes `"audio"`, excluding superseded preview snapshots and meta-routers. See [`results/summary.md`](results/summary.md) for the exact list with per-model results.

## Samples

Four short (20-30 second) dictation recordings of everyday prose — no acronyms, code, numbers-as-digits, or other elements that invite formatting ambiguity between verbatim and cleaned transcription. This is deliberate: the eval measures **audio understanding**, not prompt-following for formatting.

Each sample is paired with a `*.reference.txt` file containing the exact ground-truth text that was read aloud.

Recording conditions:
- Quiet indoor room, USB condenser mic (EMEET OfficeCore M1A)
- 16-bit PCM, mono, 16 kHz source — matches the native rate of most audio-LLM encoders, so no upstream resampling is introduced
- Natural dictation pace, no self-corrections

## Encoding

Each source WAV is re-encoded into five MP3 variants using `pydub` (LAME) at constant bitrates of **16, 24, 32, 48, 64 kbps**. Channel and sample rate are held at mono / 16 kHz across all variants so bitrate is the only independent variable. The exact encoded bytes used for each API call are preserved in [`variants/`](variants/).

## Prompt

A dedicated verbatim-transcription system prompt is used — **not** the cleanup/polish prompts typical of dictation apps:

```
Transcribe the audio VERBATIM.

- Write exactly what was said, word for word, in the order spoken.
- Keep filler words ("um", "uh", "like", "you know") and false starts.
- Do NOT remove repetitions, self-corrections, or incomplete sentences.
- Do NOT rephrase, summarize, or reformat.
- Do NOT add headings, bullets, paragraphs, or markdown.
- Add only basic sentence punctuation (periods, commas, question marks) and capitalization at sentence starts.
- Output plain text only. No preamble, no commentary.
```

This isolates audio-encoding effects from prompt-driven editorial variance. An error in the output reflects what the model misheard, not what it chose to reword.

## Scoring — Word Error Rate

Classic Levenshtein edit distance computed over whitespace-split word tokens after lowercasing. `WER = edits / len(reference_words)`. Perfect transcription is `0.000`; a totally wrong transcription the same length as the reference would score around `1.0` (can exceed 1.0 if the hypothesis is much longer).

No stemming, no punctuation stripping beyond lowercasing — this keeps the metric literal. Minor punctuation disagreements register as errors; that's acceptable because it affects all bitrates equally and cancels out in comparative analysis.

## Latency

Wall-clock time from POST → full response parsed, measured on the client side. Includes network round-trip (Israel → OpenRouter → upstream provider). Not a pure model-inference metric but it's what actually matters for dictation UX.

Each (model, sample, bitrate) cell is a single measurement; latency is noisy and should be read as indicative rather than precise. The `all.csv` contains every raw measurement for anyone wanting to recompute with different aggregations.

## Caveats

- **n=4 samples per cell** — enough to spot obvious differences, not enough for tight confidence intervals on small deltas.
- **Single-speaker, English, clear audio** — results may not generalize to accented speech, noisy environments, or languages other than English.
- **Single recording session** — all four samples are the same speaker, same mic, same room. Speaker/mic-varying effects are not captured.
- **OpenRouter routing** — OR picks the upstream provider at call time. For Gemini models that's Google directly; for GPT-Audio it's OpenAI; for others it may vary. We treat "the OpenRouter-accessible version of model X" as the unit of analysis, which is the practical unit most API users care about.
- **Pricing / availability drift** — OpenRouter's catalog changes. The model list and pricing referenced in companion docs is a point-in-time snapshot.

## Reproducibility

See [`reproduce.md`](reproduce.md).
