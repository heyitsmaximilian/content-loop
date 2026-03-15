# Content Loop 🔄

**Self-improving TikTok content that gets better with every post.**

Instead of posting and hoping, this system creates → posts → measures → learns → creates better content automatically. Each day's posts are informed by data from the previous days, creating a feedback loop that continuously optimizes for what actually works.

```
   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
   │   CREATE    │───▶│    POST     │───▶│   MEASURE   │
   │  slideshow  │    │ to TikTok   │    │ performance │
   └─────────────┘    └─────────────┘    └─────────────┘
          ▲                                       │
          │           ┌─────────────┐             │
          └───────────│    LEARN    │◀────────────┘
                      │ & improve   │
                      └─────────────┘
```

## Why This Matters

- **Most content creators guess** → You use data
- **Most optimize for views** → You optimize for conversions
- **Most post the same content forever** → Your content evolves daily
- **Most track vanity metrics** → You track revenue

## Quick Start

1. **Clone this repo**
   ```bash
   git clone <this-repo>
   cd content-loop
   ```

2. **Set up your OpenClaw agent**
   - Install the content-creator skill: Copy `skills/content-creator/` to your OpenClaw skills directory
   - Load the agent instructions: `agent/AGENT.md`

3. **Configure your brand**
   - Edit `knowledge/voice.md` with your brand voice
   - Update `knowledge/hooks.md` with hooks relevant to your niche
   - Customize `knowledge/images.md` for your image style

4. **Set up analytics** (optional but recommended)
   - For basic analytics: The system scrapes TikTok metrics automatically
   - For conversion tracking: Connect Postiz for detailed analytics

5. **Start creating**
   - Your agent will read the knowledge files and create content
   - Post performance gets logged to `data/run-log.jsonl`
   - Run the daily analysis to see what's working

## How It Works

### 🎯 Experiment Framework

The `autoresearch/` directory contains the intelligence layer:

- **experiment.py** → Defines A/B tests (hook A vs hook B, image style X vs Y)
- **analyze.py** → Pulls 3 days of performance data, identifies winners/losers
- **amend.py** → Updates knowledge files based on what's working

### 📚 Knowledge Base

Your agent reads these files before creating content:

- **hooks.md** → Hook patterns with performance history
- **images.md** → Image styles and what converts
- **ctas.md** → Call-to-action variants and their success rates
- **voice.md** → Brand voice (swap this for any product)

### 🤖 Self-Improvement

Each morning, the system:
1. Analyzes yesterday's posts
2. Identifies what worked vs what didn't
3. Updates the knowledge files automatically
4. Suggests better content for today

**Example:** If "person+conflict" hooks consistently get 5x more views than "POV format", the system automatically promotes person+conflict and demotes POV in the knowledge base.

## The Data That Drives Decisions

Every post logs performance data to `data/run-log.jsonl`:

```json
{"timestamp":"2026-03-10T09:00:00Z","type":"post","hook":"person-conflict","variant":"A","views":45000,"likes":1200,"comments":45,"shares":89,"conversion":4}
```

The analysis engine identifies patterns:
- **High views + High conversions** → Scale it (create variations)
- **High views + Low conversions** → Hook works, CTA needs fixing
- **Low views + High conversions** → Content converts, hook needs work
- **Low views + Low conversions** → Full reset needed

## Analytics Options

**Basic (included):** TikTok metrics scraped automatically
- Views, likes, comments, shares per post
- Tracks content performance over time
- Identifies trending hooks and formats

**Advanced (optional):** Connect Postiz for deeper insights
- Cross-platform analytics (Instagram, YouTube, etc.)
- Conversion tracking integration
- Automated posting workflows

## Plug In Any Agent

The autoresearch loop is **decoupled from the content skill**. The included TikTok slideshow skill is just a reference implementation. You can swap in any agent that:

1. **Reads knowledge files** before creating output
2. **Logs results** to `data/run-log.jsonl` with the standard schema
3. **Accepts amendments** to its knowledge base

### Examples of What You Could Plug In

| Domain | Skill swap | Knowledge files |
|--------|-----------|-----------------|
| **TikTok slideshows** (included) | `skills/content-creator/` | hooks, images, CTAs, voice |
| **X/Twitter threads** | Your thread-writing skill | hooks, thread structures, posting times |
| **Email campaigns** | Email copywriting skill | subject lines, CTAs, send times, segments |
| **Ad copy** | Ad generation skill | headlines, descriptions, audiences, bids |
| **Blog/SEO content** | Long-form writing skill | titles, structures, keywords, CTAs |
| **Sales outreach** | Cold email skill | openers, value props, CTAs, follow-up timing |
| **Product descriptions** | E-commerce copy skill | formats, keywords, tones, price framing |

### How to Swap

1. **Replace `skills/content-creator/`** with your own skill
2. **Replace `knowledge/*.md`** with domain-relevant knowledge files (keep the same pattern: categories + performance tracking)
3. **Update `agent/AGENT.md`** to reference your skill and knowledge files
4. **Keep `autoresearch/` unchanged** — the experiment → analyze → amend loop works on any `run-log.jsonl` data

The run-log schema is intentionally generic:
```json
{
  "timestamp": "ISO-8601",
  "type": "post|analysis|amendment",
  "hook": "variant category",
  "variant": "specific variant ID",
  "views": 0,
  "likes": 0,
  "comments": 0,
  "shares": 0,
  "conversion": 0
}
```

Add custom fields for your domain — the analyzer reads whatever's in the log. The core contract is: **log what you did → measure how it performed → amend what you know**.

## Framework Flexibility

This isn't just for TikTok or just for apps. Swap the components for any product:

- **SaaS product?** Update `voice.md` and `hooks.md` for your industry
- **Physical product?** Customize `images.md` for your product shots
- **Service business?** Adapt `ctas.md` for lead generation

The feedback loop works the same: create → post → measure → learn → improve.

## File Structure

```
content-loop/
├── skills/content-creator/     # Simplified content creation skill
├── autoresearch/              # Analysis and improvement engine
├── knowledge/                 # What the agent learns from (editable)
├── data/                     # Performance logs and history
├── agent/                    # Agent instructions and workflow
└── crons/                    # Daily analysis scheduling
```

## What Makes This Different

**Traditional approach:**
1. Create content based on "best practices"
2. Post consistently
3. Hope for the best
4. Repeat forever

**Content Loop approach:**
1. Create content based on your specific audience data
2. Post and measure precise performance metrics
3. Automatically identify what works vs what doesn't
4. Update creation guidelines based on real performance
5. Next day's content is informed by yesterday's data

## Success Metrics

Track what matters:
- **Views** → Are people watching?
- **Engagement** → Are people interacting?
- **Conversions** → Are people taking action?
- **Improvement Rate** → Is content getting better over time?

## Getting Started

Your OpenClaw agent will handle the technical details. You focus on:
1. Setting your brand voice
2. Reviewing daily performance reports  
3. Approving knowledge base updates
4. Celebrating the wins

The system handles content creation, posting analysis, and continuous improvement automatically.

---

*Built for OpenClaw agents • Optimizes for revenue, not vanity metrics • Gets smarter with every post*