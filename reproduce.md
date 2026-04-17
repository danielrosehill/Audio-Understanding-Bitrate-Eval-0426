# Reproducing the eval

The eval was run using the `evals/full_sweep.py` script from the [Multimodal Voice Typer](https://github.com/danielrosehill/AI-Typer-V2) repo. To reproduce:

## 1. Clone the tooling repo

```bash
git clone https://github.com/danielrosehill/AI-Typer-V2.git
cd AI-Typer-V2
./build.sh --dev    # builds venv under app/.venv
```

## 2. Drop in the samples

From this eval repo:

```bash
cp samples/*.wav samples/*.reference.txt \
   <path-to-AI-Typer-V2>/evals/samples/
```

Or record your own — any 16-bit mono PCM WAV plus a paired `<name>.reference.txt` of the ground-truth spoken text will work.

## 3. Set your API key

```bash
export OPENROUTER_API_KEY=sk-or-v1-...
```

## 4. Run the sweep

From the AI-Typer-V2 repo root:

```bash
# Default: all 12 models × all samples × 5 bitrates (16, 24, 32, 48, 64)
./app/.venv/bin/python3 -m evals.full_sweep

# Narrower sweep — e.g. just two models, one sample
./app/.venv/bin/python3 -m evals.full_sweep \
    --models google/gemini-3-flash-preview mistralai/voxtral-small-24b-2507 \
    --samples 1 \
    --bitrates 24 32 64

# Dry run (prints plan, skips API calls)
./app/.venv/bin/python3 -m evals.full_sweep --dry-run
```

Output lands in `evals/results/full-sweep-<DDMM-HHMMSS>/` with the same structure as this repo's `results/`.

## 5. Estimated cost

At April 2026 OpenRouter prices, a full 12-model × 4-sample × 5-bitrate = 240-call sweep runs about **$0.20-$0.30**. Cheap models (Gemini 2.0 Flash Lite, Voxtral) are sub-cent each; Gemini 2.5 Pro and the GPT-Audio tier dominate the cost.

## 6. Differences you might see

- **WER variance**: Audio LLMs are non-deterministic at `temperature=default`. Expect WER to wiggle by ±0.01-0.02 on re-runs for a given cell.
- **Latency**: OR routes to different upstream providers at different times; cold-start vs. warm-pool effects are visible. Expect latency values to vary by 20-50%.
- **OpenAI conversationalization**: the GPT-Audio family occasionally interprets the audio as conversational input and *responds* to it instead of transcribing. This is a prompt-following quirk of those models, not audio quality. See the `results/openai__*/` transcripts for examples.
