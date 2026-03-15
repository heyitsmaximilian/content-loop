# Image Style Guide

Visual consistency and authenticity are critical for stopping the scroll. These guidelines are based on performance data and continuously refined.

## Style Foundation

### Base Prompt Template
```
iPhone photo of [scene description], [style specifics], realistic lighting, natural colors, taken on iPhone 15 Pro. Portrait orientation 1024x1536. [Consistency anchors]. No text, no watermarks, no logos.
```

### Consistency Anchors
Lock these elements across all 6 slides to maintain visual continuity:

**Architecture:**
- Same room layout and proportions
- Same window placement and size
- Same architectural details (molding, fixtures)
- Same flooring type and color

**Lighting & Atmosphere:**
- Same time of day (golden hour, natural daylight, etc.)
- Same light direction and quality
- Same color temperature (warm vs cool)
- Same shadow patterns

**Perspective & Framing:**
- Same camera height and angle
- Same field of view
- Same compositional structure
- Same foreground/background relationship

## Proven Style Categories

### 🏆 HIGH PERFORMING STYLES

#### Modern Apartment Aesthetic
- **Description**: Clean, contemporary spaces with warm lighting
- **Key Elements**: Neutral colors, minimal furniture, plants, natural textures
- **Performance**: 35K avg views, 7.8% engagement
- **Prompt Addition**: "Modern apartment interior, Scandinavian-inspired, warm natural lighting"
- **Consistency Locks**: "Large window on left wall, light wooden floors, white walls with subtle texture"

#### Cozy Transformation Look
- **Description**: Lived-in spaces with personality and warmth
- **Key Elements**: Layered textures, warm colors, personal touches, soft lighting
- **Performance**: 28K avg views, 6.9% engagement  
- **Prompt Addition**: "Cozy, lived-in aesthetic, warm lamp lighting, layered textures"
- **Consistency Locks**: "Corner reading nook, exposed brick accent wall, hardwood floors"

#### Before/After Contrast
- **Description**: Clear visual progression showing improvement
- **Key Elements**: Same space, dramatically different styling, lighting changes
- **Performance**: 31K avg views, 8.2% engagement
- **Prompt Addition**: "Same apartment layout, [before: basic/sparse] [after: styled/decorated]"
- **Consistency Locks**: "Identical room layout, same window placement, same architectural features"

### 🧪 TESTING STYLES

#### Luxury Aspiration
- **Description**: Higher-end finishes and furniture
- **Performance**: 18K avg views, 5.4% engagement (limited data)
- **Prompt Addition**: "Upscale apartment interior, designer furniture, premium finishes"

#### Small Space Solutions  
- **Description**: Compact, efficient layouts with clever storage
- **Performance**: 22K avg views, 6.1% engagement (limited data)
- **Prompt Addition**: "Small studio apartment, space-saving solutions, efficient layout"

### ❌ POOR PERFORMING STYLES

#### Stock Photo Generic
- **Description**: Overly polished, unrealistic perfection
- **Performance**: 5K avg views, 2.1% engagement
- **Problem**: Looks fake, doesn't connect emotionally

#### Dark/Moody Aesthetic  
- **Description**: Low lighting, dramatic shadows
- **Performance**: 8K avg views, 3.2% engagement
- **Problem**: Hard to see details on mobile screens

## Technical Specifications

### Aspect Ratio & Dimensions
- **Portrait Only**: 1024x1536 pixels (9:16 ratio)
- **File Format**: PNG for text overlays, JPEG for final posts
- **Quality**: High resolution for crisp mobile viewing

### Image Generation Settings

#### OpenAI (Recommended)
- **Model**: gpt-image-1.5 (never gpt-image-1)
- **Quality**: "hd" setting
- **Style**: Natural/realistic (avoid "vivid" for authenticity)

#### Consistency Prompting Strategy
1. **Start with identical base description** for all 6 slides
2. **Add specific changes only** for transformation/progression
3. **Repeat consistency anchors** in every prompt
4. **Use specific measurements** ("8-foot ceiling", "12x10 room")

### Text Overlay Zones

#### Safe Zones for Text
- **Primary Text Area**: 20-40% from top (avoids status bar, leaves room for TikTok controls)
- **Secondary Text**: 45-65% from top (for subtitle or emphasis)
- **Avoid Bottom 20%**: TikTok UI covers this area

#### Text Readability Requirements
- **High contrast**: White text with thick black outline
- **Font size**: 6.5% of image width minimum
- **Line spacing**: 1.3x font height for readability
- **Maximum 4 lines**: More lines get too small on mobile

## Performance Insights

### What Stops the Scroll
1. **Realistic authenticity** → Looks like someone actually lives there
2. **Clear transformation** → Obvious before/after or progression
3. **Aspirational but achievable** → Nice enough to want, realistic enough to believe
4. **Personal details** → Books, plants, coffee mugs, lived-in touches

### What Gets Skipped
1. **Obviously AI-generated** → Perfect, sterile, unrealistic lighting
2. **Inconsistent between slides** → Each slide looks like a different room
3. **Too dark or busy** → Hard to see details while scrolling
4. **Generic stock photo feel** → No personality or character

### Mobile-First Considerations
- **Large, clear focal points** → Details visible on small screens
- **High contrast** → Works in bright sunlight or dark rooms  
- **Simple compositions** → Easy to parse while scrolling quickly
- **Portrait framing** → Fills the TikTok screen completely

## Style Evolution

The autoresearch system tracks which visual elements correlate with performance:

### Recent Learnings
- **Natural lighting performs 40% better** than artificial/dramatic lighting
- **Warm color palettes get 25% more engagement** than cool/minimal
- **Visible everyday objects increase relatability** by 30%
- **Consistent architectural details across slides boost completion rates** by 18%

### Testing Queue
1. Different times of day (golden hour vs midday)
2. Seasonal elements (spring plants, winter textures)
3. Room types (bedroom, kitchen, living room focus)
4. Cultural aesthetics (Scandinavian, Japanese, industrial)

---

## Quick Reference Checklist

Before generating images:
- [ ] Portrait orientation (1024x1536)
- [ ] Consistent base room description
- [ ] Locked architectural elements  
- [ ] Realistic lighting specified
- [ ] "iPhone photo" in prompt
- [ ] No text/watermarks mentioned
- [ ] Everyday details included
- [ ] Safe zones considered for text overlay

*This guide updates automatically based on your visual performance data.*