# Content Loop

**Automated content factory with a self-improving feedback loop.**

Generate animated short-form social content (TikTok / Reels / Shorts) using AI-powered mascot characters — then measure, learn, and improve automatically.

```
Topic → Script → Images → Video → Assembly → QA → Publish → Measure → Learn
  │                                                                      │
  └──────────────────────── feedback loop ◀──────────────────────────────┘
```

## What This Does

1. **Creates content** — Claude writes scripts, image models generate character scenes, video models animate them, FFmpeg assembles the final cut with voiceover and captions
2. **Maintains character consistency** — LoRA-trained mascots that look identical across hundreds of generations
3. **Enforces compliance** — tiered review system from entertainment (auto-publish) to regulated health content (human-required)
4. **Learns from performance** — daily analysis identifies winning hooks, formats, and styles; automatically updates the knowledge base
5. **Works across products** — configure once per brand, reuse the entire pipeline

## Quick Start

```bash
git clone https://github.com/heyitsmaximilian/content-loop.git
cd content-loop
pip install pyyaml

# Set up a product (or use the included Cadence example)
cp -r products/_template products/my-product
# Edit products/my-product/product.yaml and characters/

# Generate a script (dry run — no image/video generation)
python pipeline/orchestrator.py --product cadence --topic "GLP-1 and muscle preservation" --dry-run

# Full pipeline (requires API keys in .env)
python pipeline/orchestrator.py --product cadence --topic "GLP-1 and muscle preservation"
```

## Architecture

```
content-loop/
├── pipeline/                    # Content generation pipeline
│   ├── orchestrator.py          # Runs the full pipeline for one content piece
│   ├── agents/
│   │   ├── script_agent.py      # Claude API → structured script JSON
│   │   ├── image_agent.py       # Leonardo AI (LoRA) → character scene images
│   │   ├── video_agent.py       # Kling / Runway → animated clips
│   │   ├── audio_agent.py       # ElevenLabs → voiceover
│   │   ├── assembly.py          # FFmpeg → final video with captions
│   │   └── qa_agent.py          # Quality scoring + publish decision
│   ├── models/
│   │   └── schemas.py           # Data objects (TopicBrief, Script, AssetManifest, etc.)
│   └── compliance/
│       └── checker.py           # Claim review + policy enforcement
│
├── products/                    # Per-product configuration
│   ├── _template/               # Copy this to create a new product
│   │   ├── product.yaml         # Brand voice, compliance tier, content strategy
│   │   └── characters/
│   │       └── template.yaml    # Character bible, expressions, poses, prompts
│   ├── cadence/                 # Cadence (GLP-1 wellness app)
│   │   ├── product.yaml
│   │   └── characters/jab.yaml  # "Jab" the syringe mascot
│   └── mogged/                  # Mogged (looksmaxxing app) — TODO
│
├── formats/
│   └── library.yaml             # Reusable content archetypes (explainer, myth_bust, etc.)
│
├── autoresearch/                # Self-improvement engine
│   ├── analyze.py               # Performance analysis (winners/losers)
│   ├── experiment.py            # A/B testing framework
│   ├── amend.py                 # Auto-updates knowledge files based on data
│   ├── meta.py                  # Meta-learning (detects skill degradation)
│   └── config.py                # Config loader
│
├── knowledge/                   # Generic knowledge base (hooks, CTAs, images)
│   └── cadence/                 # Product-specific knowledge
│
├── data/                        # Logs, reports, pipeline runs
│   ├── run-log.jsonl            # Post performance data
│   └── runs/                    # Pipeline output per content piece
│
├── crons/
│   └── daily-review.sh          # Daily analysis + knowledge updates
│
├── config.yaml                  # Active product + analysis settings
└── .env                         # API keys (not committed)
```

## Adding a New Product

```bash
# 1. Copy the template
cp -r products/_template products/your-product

# 2. Fill in product.yaml
#    - Brand voice, compliance tier, audience, content strategy

# 3. Create a character
cp products/_template/characters/template.yaml products/your-product/characters/mascot.yaml
#    - Visual design, expressions, poses, prompt fragments, voice profile

# 4. Set the active product
# Edit config.yaml: product: your-product

# 5. Generate content
python pipeline/orchestrator.py --product your-product --topic "your topic"
```

## Content Formats

Pre-built archetypes in `formats/library.yaml`:

| Format | Duration | Best For |
|--------|----------|----------|
| **Explainer** | 20-45s | Teaching one concept clearly |
| **Myth Bust** | 15-30s | Correcting misconceptions |
| **Listicle** | 30-60s | Tips, signs, mistakes lists |
| **Mini Skit** | 10-30s | Comedy, personality building |
| **Day in the Life** | 15-30s | Routine content, product integration |
| **Worldbuilding** | 15-45s | Serialized stories, lore |
| **Trend Adaptation** | 10-20s | Riding trending sounds/formats |
| **Reaction Clip** | 10-25s | Reacting to claims or content |

## Compliance Tiers

| Tier | Auto-publish? | Human Review | Example |
|------|--------------|--------------|---------|
| **Low** | Yes (QA > 0.7) | Optional | Entertainment, memes, lifestyle tips |
| **Medium** | After human glance | Light review | Consumer product features, general advice |
| **High** | Never | Required | Health/wellness claims, anything medical-adjacent |
| **Regulated** | Never | Legal + compliance | Drug info, financial advice, regulated industries |

## Tech Stack

| Component | Tool | Purpose |
|-----------|------|---------|
| Scripting | Claude API | Script generation with brand voice rules |
| Images | Leonardo AI (LoRA) | Character-consistent scene generation |
| Images (fallback) | GPT-image-1.5 | Creative exploration, one-off variations |
| Video (volume) | Kling 2.6 | Daily content, image-to-video animation |
| Video (hero) | Runway Gen-4.5 | High-fidelity hero content |
| Voice | ElevenLabs | Character voiceover |
| Assembly | FFmpeg | Stitch clips + audio + captions |
| Analysis | autoresearch/ | Performance tracking + self-improvement |

## The Feedback Loop

```
Day 1: Post content → log to run-log.jsonl
Day 2: Daily review analyzes performance → identifies winners/losers
Day 3: Knowledge base updated → script agent uses new learnings
Day 4: Better content → higher performance → loop continues
```

The analysis engine (`autoresearch/`) tracks:
- Which hook categories drive views
- Which formats drive engagement
- Which CTAs drive conversions
- Which visual styles perform best

Winners get promoted. Losers get demoted. Knowledge files update automatically.

## Environment Variables

Create a `.env` file in the repo root:

```bash
ANTHROPIC_API_KEY=sk-...
LEONARDO_API_KEY=...
ELEVENLABS_API_KEY=...
KLING_API_KEY=...
RUNWAY_API_KEY=...        # Optional, for hero content
OPENAI_API_KEY=...        # Optional, for GPT-image fallback and Sora
```

## Current Status

- [x] Analysis engine (experiment → analyze → amend → meta-learn)
- [x] Product configuration system (multi-brand)
- [x] Character system (bible + expressions + poses + LoRA + prompts)
- [x] Content format library (8 archetypes)
- [x] Pipeline orchestrator + agent architecture
- [x] Compliance checker (tiered)
- [x] QA scoring + publish decisions
- [ ] Wire script agent to Claude API
- [ ] Wire image agent to Leonardo API
- [ ] Wire video agent to Kling/Runway API
- [ ] Wire audio agent to ElevenLabs API
- [ ] FFmpeg assembly implementation
- [ ] Train first LoRA (Jab character for Cadence)
- [ ] Publishing agent (TikTok / Reels / Shorts APIs)
- [ ] Trend detection agent
