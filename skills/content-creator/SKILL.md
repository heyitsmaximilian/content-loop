---
name: content-creator
description: Creates TikTok slideshows with intelligent hooks, consistent image styles, and performance tracking. Reads knowledge files to learn from previous performance and continuously improve content quality. Use when creating social media content, running content experiments, or building self-improving marketing campaigns.
---

# Content Creator

Creates TikTok slideshows that get better with every post. This skill reads your knowledge base (hooks, image styles, CTAs, brand voice) and generates content accordingly, logging performance for continuous improvement.

## Prerequisites

The skill expects these knowledge files to exist (created during setup):
- `knowledge/hooks.md` - Hook patterns with performance data
- `knowledge/images.md` - Image style guidelines and what works
- `knowledge/ctas.md` - Call-to-action variants and conversion rates  
- `knowledge/voice.md` - Brand voice and messaging guidelines

## Core Functions

### 1. Content Generation

**Read knowledge files first** - always check the current knowledge base before creating:

```javascript
// Read current knowledge state
const hooks = await readFile('knowledge/hooks.md');
const imageStyle = await readFile('knowledge/images.md');
const ctas = await readFile('knowledge/ctas.md');
const voice = await readFile('knowledge/voice.md');
```

**Select optimal hook** based on performance data in hooks.md:
- Prioritize hooks marked as "HIGH PERFORMER"
- Avoid hooks marked as "DROPPED"
- Test hooks marked as "TESTING" occasionally

**Generate slideshow structure:**
1. **Slide 1** - Hook that stops the scroll
2. **Slide 2** - Problem/situation setup
3. **Slide 3** - Discovery/solution introduction  
4. **Slide 4** - Product/app demonstration
5. **Slide 5** - Amazing result/transformation
6. **Slide 6** - Clear CTA based on best-performing variants

### 2. Image Generation

**Consistency is critical** - all 6 slides should look like they belong together:

```
Base prompt template from images.md:
"iPhone photo of [scene], [style details], realistic lighting, natural colors, 
taken on iPhone 15 Pro. Portrait orientation 1024x1536. 
[Consistency anchors: same room layout, same lighting, same perspective]"
```

**Key rules:**
- Portrait aspect ratio (1024x1536) for TikTok
- Lock architectural details across all slides
- Use "iPhone photo" + "realistic lighting" for authenticity
- Include everyday details (mugs, books, plants) for lived-in feel
- No text or watermarks in generated images

### 3. Text Overlays

Add text using the proven formula from successful posts:

**Text styling:**
- Dynamic font sizing: 6.5% of image width for medium text
- White text with thick black outline (15% of font size)
- Positioned at 28% from top (safe zone)
- Manual line breaks: 4-6 words per line maximum

**Content style:**
- Reactions, not descriptions ("Wait... this actually works?" vs "Modern design")
- Conversational tone matching voice.md
- 3-4 lines per slide ideal
- Build narrative tension across slides

### 4. Performance Logging

After creating content, log the attempt to `data/run-log.jsonl`:

```json
{
  "timestamp": "2026-03-15T14:30:00Z",
  "type": "content_created",
  "hook_category": "person-conflict",
  "hook_text": "My landlord said I can't renovate",
  "image_style": "modern-apartment",
  "cta_variant": "link-in-bio-direct",
  "experiment_id": "hook_test_A1",
  "status": "ready_to_post"
}
```

## Hook Categories (Examples)

Based on proven performance patterns:

### HIGH PERFORMERS
- **Person + Conflict**: "My boyfriend said our apartment looks boring"
- **Challenge Format**: "She said you can't change anything... challenge accepted" 
- **Before/After Reveal**: "I showed my mom what AI thinks our kitchen should look like"

### TESTING
- **Listicle**: "3 things that made my small space look huge"
- **POV Format**: "POV: You discover there's an app for this"

### DROPPED (Poor performance)
- **Direct Ads**: "Try this amazing app"
- **Price Comparisons**: "Why spend $1000 when you can..."

## Success Patterns

**What works:**
- Personal stories with conflict/tension
- Gradual reveals building to transformation
- Authentic "discovered this accidentally" framing
- Clear but subtle product integration
- Strong visual consistency across slides

**What doesn't work:**
- Obvious advertising language
- Generic stock photo aesthetics  
- Inconsistent image styles between slides
- Weak or buried CTAs
- No hook/story structure

## Workflow Integration

1. **Before creating** - Read all knowledge files to understand current best practices
2. **During creation** - Follow image consistency rules and hook performance data
3. **After creating** - Log attempt with all relevant metadata
4. **Post-posting** - Performance data flows back through the autoresearch system

The autoresearch tools (`experiment.py`, `analyze.py`, `amend.py`) will analyze performance and update the knowledge files. Your next content creation will benefit from these learnings.

## Example Usage

```
Agent prompt: "Create a TikTok slideshow for [product] targeting [audience]"

1. Read knowledge/ files to understand current best practices
2. Select highest-performing hook category from hooks.md
3. Generate 6 consistent images following images.md guidelines
4. Add text overlays using voice.md tone and proven CTA from ctas.md
5. Log creation details to data/run-log.jsonl
6. Output final slideshow ready for posting
```

## Knowledge File Updates

The skill reads but does not write knowledge files. Updates come from:
- Manual editing by user
- Automated updates via `autoresearch/amend.py` based on performance analysis
- Periodic reviews and optimizations

This ensures content creation always uses the latest learnings while maintaining human oversight of the knowledge base evolution.

## Error Handling

**Missing knowledge files** → Create with defaults and warn user
**Inconsistent image generation** → Retry with stronger consistency prompts
**Poor hook selection** → Fall back to proven high-performers from hooks.md
**Failed text overlay** → Adjust font sizing and try simpler layout

The skill prioritizes creating usable content over perfect content - better to post something good than nothing at all.

---

*This skill gets smarter over time as your knowledge base evolves based on real performance data.*