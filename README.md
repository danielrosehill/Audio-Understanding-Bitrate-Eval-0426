# Audio Understanding — MP3 Bitrate Evaluation (April 2026)

Empirical eval measuring how MP3 compression bitrate affects transcription accuracy across every audio-input LLM available on [OpenRouter](https://openrouter.ai).

**Question**: If you're sending voice dictation audio to a multimodal LLM, how low can you drop the MP3 bitrate before transcription accuracy degrades?

**TL;DR**: _(populated after the run completes — see [`results/summary.md`](results/summary.md))_

## Why this eval exists

Most guidance on audio bitrates for ML (e.g. Whisper, Deepgram) assumes you're feeding audio to a dedicated ASR model. Audio-input LLMs (Gemini's audio-capable tiers, GPT-Audio, Voxtral, MiMo) are a different animal — they tokenize audio through their own encoders and the behavior vs. bitrate isn't well characterized in public benchmarks.

This eval produces that characterization for the OpenRouter-accessible set, across **12 models × 4 dictation samples × 5 bitrates = 240 API calls**.

## What's in this repo

| Path | Contents |
|---|---|
| `samples/` | The 4 source recordings (WAV, 16-bit mono 16 kHz) with paired `.reference.txt` ground-truth transcripts |
| `variants/` | Pre-encoded MP3 copies of each sample at 16, 24, 32, 48, 64 kbps — the exact bytes sent to each API |
| `results/all.csv` | Machine-readable results: `model, sample, bitrate_kbps, payload_kb, elapsed_s, wer, error` |
| `results/summary.md` | Aggregated WER × latency table (model × bitrate) |
| `results/<model>/<sample>/` | Per-(model, sample) breakdown with full transcription text at each bitrate |
| `methodology.md` | How the eval was run — prompt, scoring, encoding pipeline, caveats |
| `reproduce.md` | How to re-run the eval on your own hardware/key |

## Dataset availability

The same content is mirrored as a Hugging Face dataset:
[`danielrosehill/Audio-Understanding-Bitrate-Eval-0426`](https://huggingface.co/datasets/danielrosehill/Audio-Understanding-Bitrate-Eval-0426)

The GitHub repo is the source of truth for methodology and code; the HF dataset is a packaged distribution for `datasets.load_dataset()` workflows.

## Tooling

The eval was run from the [Multimodal Voice Typer](https://github.com/danielrosehill/AI-Typer-V2) repo (`evals/full_sweep.py`), which is the voice-dictation app the findings feed back into.

## License

Code, results, and documentation: [MIT](LICENSE).
Audio samples: CC0 — public domain, do whatever you want with them.

## Citation

If this is useful in your work, a link back to either the GitHub repo or the HF dataset is appreciated but not required.

```
Rosehill, D. (2026). Audio Understanding — MP3 Bitrate Evaluation.
https://github.com/danielrosehill/Audio-Understanding-Bitrate-Eval-0426
```
