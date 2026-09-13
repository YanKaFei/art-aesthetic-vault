<div align="center">

# Art Aesthetic Style Library

**141 art movements, decomposed into swappable AI prompt layers**

Byzantine to Y2K ｜ East & South Asia · Islamic ｜ Photography ｜ Digital subcultures

177 notes · 654 public-domain images · 33 ready-to-run scripts

**English** ｜ [中文](README.md)

</div>

---

## What is this

Most "art style reference" collections are just image folders. You save a few hundred
pictures, and then when it's time to actually use them you don't know what to look at
or how to describe it. The images are dead weight.

This library does something different: **it breaks each movement's visual language into
seven layers that can be swapped independently.**

```
Subject  +  Style  +  Lighting  +  Color
         +  Composition  +  Medium  +  Mood  +  Camera
```

Once it's layered, you can take the **lighting** from one painting and put it on the
**subject** of a completely different one. That's what a reference library is actually for.

> ### A note on language
> **The prompt layers are already in English** - they're what you paste into a model.
> Only the explanations (visual breakdowns, pitfalls, why-it-works notes) are in Chinese.
> If you only want the prompts, you can use this library as-is.

### See it work

Say you want a bounty hunter in a neon-lit alley, but with classical painting light:

```
python3 artvault.py compose "雨夜霓虹街头的赏金猎人，要巴洛克的光照，赛博朋克的构图" --subject "a female bounty hunter in a wet neon alley"
```

It recognises that "巴洛克" (Baroque) is followed by "光照" (lighting) and takes
Baroque's lighting layer; Cyberpunk supplies style and composition. Output:

```
a female bounty hunter in a wet neon alley,             <- your subject
cyberpunk, neo-noir concept art, dense neon signage,    <- Style layer (Cyberpunk)
single hard light source from off-frame,                <- Lighting layer (Baroque)
deep crushed shadows, candlelight rim light,
cyan and magenta clash, amber accent, deep black,       <- Color layer (Cyberpunk)
low angle looking up at megastructures,                 <- Composition layer (Cyberpunk)
alienated, oppressive, intoxicating                     <- Mood layer
```

**Same subject, every layer independently replaceable.** That's the difference between
this and piling up style keywords.

---

## Skill tree

```
Art Aesthetic Style Library
│
├─ Western Classical & Modern · 47
│  ├─ Medieval & Byzantine
│  │  ├ Byzantine Art . Romanesque . Gothic Art
│  │  └ International Gothic
│  ├─ Renaissance
│  │  ├ Early Renaissance . Renaissance . Early Netherlandish
│  │  └ Venetian School . Mannerism
│  ├─ Baroque & Classical
│  │  ├ Baroque . Caravaggisti . Dutch Golden Age
│  │  └ Rococo . Classicism . Neoclassicism
│  ├─ 19th Century
│  │  ├ Romanticism . Realism . Naturalism
│  │  └ Orientalism . Academic Art . Pre-Raphaelite
│  ├─ Impressionism & After
│  │  ├ Impressionism . Neo-Impressionism . Post-Impressionism
│  │  └ Les Nabis . Symbolism . Japonism
│  ├─ Fin de Siecle
│  │  └ Art Nouveau . Vienna Secession . Arts and Crafts
│  └─ American & Modern Schools
│      ├ Hudson River School . Luminism . Tonalism
│      ├ Ashcan School . American Realism . Regionalism
│      ├ Precisionism . Social Realism . Socialist Realism
│      ├ Muralism . Magic Realism . Metaphysical Art
│      ├ Neo-Romanticism . Naïve Art (Primitivism) . Classical Realism
│      └ Kitsch . New Objectivity
├─ East Asia · South Asia · Islam · 21
│  ├─ China
│  │  ├ Blue-Green Landscape . Ink Wash Xieyi . Gongbi
│  │  └ Song Academic Painting . Dunhuang Murals
│  ├─ Japan
│  │  ├ Ukiyo-e . Rimpa . Suiboku-ga
│  │  ├ Yamato-e . Sōsaku-hanga . Shin-hanga
│  │  └ Zen Art
│  ├─ Korea
│  │  └ Minhwa
│  ├─ Persia & Islam
│  │  ├ Persian Miniature . Safavid Painting . Mughal Miniature
│  │  └ Islamic Geometric . Arabic Calligraphy
│  ├─ Himalaya & Indigenous
│  │  └ Tibetan Thangka . Indigenism
│  └─ Others
│      └ Native Art
├─ Modernism & Post-war · 23
│  ├─ Expressionism & Fauvism
│  │  └ Expressionism . Fauvism . Der Blaue Reiter
│  ├─ Cubism & Futurism
│  │  └ Cubism . Orphism . Futurism
│  ├─ Geometric Abstraction
│  │  ├ Suprematism . Constructivism . De Stijl
│  │  └ Bauhaus
│  ├─ Dada & Surrealism
│  │  └ Dada . Surrealism
│  ├─ Post-war Abstraction
│  │  └ Abstract Expressionism . Color Field
│  ├─ Pop & Minimal
│  │  ├ Pop Art . Op Art . Minimalism
│  │  └ Art Deco
│  └─ Others
│      ├ Conceptual Art . Photorealism . Land Art
│      └ Superflat . Neo-Expressionism
├─ Digital · Subculture · Photography · 24
│  ├─ Five Punks
│  │  ├ Cyberpunk . Steampunk . Dieselpunk
│  │  └ Solarpunk . Biopunk
│  ├─ Internet Nostalgia
│  │  ├ Vaporwave . Synthwave . Pixel Art
│  │  └ Retro 90s Anime . Dreamcore . Y2K Aesthetic
│  ├─ Animation & Illustration
│  │  └ Anime Cel
│  ├─ Silver & Print
│  │  └ Cyanotype . Wet Plate Collodion . Polaroid & Film
│  ├─ Atmosphere & Living
│  │  ├ Dark Academia . Cottagecore . Wabi-Sabi
│  │  └ Gothic Subculture . Wasteland
│  ├─ Graphic Design
│  │  └ Minimalist Design . Swiss Style . Memphis Design
│  └─ Cinematic
│      └ Film Noir
├─ Avant-Garde · Contemporary · Postmodern · 20
│  ├─ The Three Umbrellas
│  │  └ Avant-Garde . Contemporary Art . Postmodernism
│  ├─ Abstract Branches
│  │  └ Abstract Art . Hard-Edge Painting . Post-Painterly Abstraction
│  ├─ Anti-Art & Kitsch
│  │  └ Neo-Dada . Neo-Pop . Transavantgarde
│  ├─ Margins & Body
│  │  └ Art Brut . Outsider Art . Feminist Art
│  ├─ Public & Space
│  │  └ Street Art . Kinetic Art . Light and Space
│  ├─ New Media & Post-Conceptual
│  │  └ Digital Art . Hyper-Realism
│  └─ Others
│      └ Art Informel . Tachisme . Lyrical Abstraction
└─ Photography & Image · 6
   ├─ Two Traditions
   │  └ Pictorialism . Straight Photography
   ├─ Social & Street
   │  └ Documentary Photography . Street Photography
   └─ Conceptual & Fashion
       └ Surrealist Photography . Fashion Editorial
```

---

## What's inside

| | |
|---|---|
| **Movement cards** | **141**, in 6 categories. Each has a 6-axis visual breakdown, 7 prompt layers, a 6-color palette, a video layer, and known failure modes |
| **Public-domain images** | **654** (232 MB), covering 81 movements |
| **Guides & methodology** | 18 notes (overview, keyword atlas, the 7-layer method, video structure, palette index, reverse-engineering toolkit...) |
| **Keyword atlas** | All **218 styles / 189 movements / 68 genres** mapped to a card |
| **Note templates** | 3 |
| **Scripts** | 21 - fetch, generate, search, compose, MCP server |

> **62 movements are "prompt-only cards."** Abstract Expressionism, Pop Art, Minimalism,
> Conceptual Art, Cyberpunk, Vaporwave and others are still in copyright, so no open data
> source will supply images. Their visual language and 7-layer structure are documented
> exactly the same way - just without pictures. This is deliberate, not a gap.

---

## How to use

### 1. As an Obsidian vault

Open the folder in Obsidian. Recommended entry points:

- `00-导航/提示词拆解方法.md` - **start here**, it explains the 7 layers
- `00-导航/流派总览.md` - overview of all 141 movements
- `10-流派/` - pick a movement, read its full breakdown
- `00-导航/关键词图谱.md` - look up any unfamiliar style term

### 2. From the command line (or let an AI drive it)

```bash
cd _scripts

python3 artvault.py categories              # 6 categories, 141 movements
python3 artvault.py search "neon rain"      # fuzzy search, Chinese or English
python3 artvault.py layers baroque          # just the 7 prompt layers
python3 artvault.py show ukiyo-e            # full card
python3 artvault.py palette cyberpunk       # 6-color palette
python3 artvault.py related cubism          # find related movements
python3 artvault.py --json layers baroque   # machine-readable
```

**The core feature is composition:**

```bash
# Explicit cross-era mixing
python3 artvault.py compose --style ukiyo-e --lighting baroque --color vaporwave --composition precisionism --subject "a lone samurai"
```

It **detects and prints layer conflicts.** When you mix movements, their negative prompts
fight each other - ukiyo-e forbids `cast shadows` while Baroque lighting *requires*
`deep crushed shadows`; Precisionism forbids `people` while your subject is a person.
**The model won't error**, it just produces subtly worse images that are very hard to debug.
This check saves hours.

### 3. Install as an AI skill (recommended)

The repo ships **two** skills, installed together:

| Skill | Purpose | Triggers when |
|---|---|---|
| `art-aesthetic-vault` | **Use** the library: search movements, pull the 7 layers, compose prompts | you ask "what style should this character be" |
| `build-art-aesthetic-vault` | **Build** a library from scratch | you say "I want one of these too" |

> [!note] Neither skill bundles data
> Both are **symlinks** into this repo - the data exists in exactly one place.
> If `mv_*.py` (141 movement definitions) were bundled into a skill there would be
> two copies, and they would drift. Measured: the bundled copy had 4 files out of
> sync with the repo, and libraries built from it had **wrong category assignments**.

```bash
cd skill && ./install.sh
```

It **symlinks** the skill into every skill directory present on your machine:

| Directory | Read by |
|---|---|
| `~/.agents/skills/` | DSH / Codex / general convention |
| `~/.claude/skills/` | Claude Code |
| `~/.codex/skills/` | Codex |

**Why symlink:** the skill resolves its own real path via `pwd -P`, derives the repo
root from it, and therefore **finds the vault wherever it lives - no configuration,
survives moving the repo**. No path is hardcoded anywhere in the skill.

```bash
./install.sh --copy        # copy instead of symlink (breaks if you move the repo)
./install.sh --uninstall   # remove
bash locate.sh             # manual vault lookup (for troubleshooting)
```

Start a **new AI session** for it to take effect.

### 4. As an MCP server (Claude Desktop / Cursor)

```json
{
  "mcpServers": {
    "artvault": {
      "command": "python3",
      "args": ["<absolute path to this repo>/_scripts/mcp_server.py"]
    }
  }
}
```

10 tools: `search_movements` `get_movement` `get_layers` `compose_prompt`
`get_palette` `find_related` `list_categories` `analyze_image` `match_movement`
`get_video_prompt`.
Pure standard library - **no `pip install mcp` needed** (the last two also need
Pillow / the CLIP model; without them they return a clear reason and the other
seven keep working).

---

## Why it's different

### 1. Not an image pack - a composable structure

An image pack gives you "what this feels like." This gives you "how to make it."
Every layer can be lifted out on its own. Swap the subject but keep the style layer,
and you have a style-transfer template.

### 2. Lighting is pulled out as its own layer

Most people write prompts as one undifferentiated blob and then debug by trial and error.
This library makes an explicit claim: **lighting affects the final texture more than the
style keywords do.** Every movement's lighting layer is a separate snippet you can drop
onto an unrelated subject.

### 3. Every movement has *targeted* negative prompts

**The specific failure modes of that movement**:

- Impressionism → `black shadows, smooth blending, photorealistic`
- Renaissance → `visible brushstrokes, impasto` (AI defaults to thick oil paint; Renaissance surfaces are smooth)
- Ukiyo-e → `3d shading, cast shadows, gradient` (AI adds volume automatically; ukiyo-e is flat)

**Note that different movements' negative prompts are often opposites** - which is exactly
why mixing them breaks, and exactly what this library manages for you.

### 4. Usable by AI, not just by you

LLMs have fuzzy memories about art movements and routinely confuse Art Nouveau with
Art Deco, or Barbizon with Impressionism. This library pins down concrete terminology
for 141 movements, so an AI calling it won't make things up.

### 5. Completeness is verifiable

The keyword atlas maps **all 218 styles / 189 movements / 68 genres** onto cards.

### 6. Public domain only - no second thoughts

All images come from CC0 / public-domain open sources. Free to use, modify,
redistribute, and train on.

### 7. Extensible

Adding a movement means adding one entry to one Python file. Image fetching, note
generation, keyword mapping and the AI interfaces all follow automatically.

---

## Quick start

```bash
git clone --depth 1 https://github.com/YanKaFei/art-aesthetic-vault.git
cd art-aesthetic-vault

# immediate self-check
cd _scripts && python3 artvault.py categories
```

**Requirements:** Python 3.8+ and Obsidian (recommended).

**The core scripts use only the Python standard library - nothing to pip install.**

Optional dependencies - everything works without them, they just add capability:

```bash
# Pinterest grabbing and the image inbox
pip3 install --user requests Pillow

# Enhanced image-analysis dimensions (face framing / Hough lines / saliency)
# and semantic search
pip3 install --target ./vendor/libs numpy opencv-python-headless
```

> Installing into `vendor/libs` keeps your system Python clean, and the
> directory is gitignored. To skip them explicitly: `ARTVAULT_NO_EXT=1`.
> Note `artvault_vision.py` is macOS-only (it uses the system Vision
> framework); elsewhere it degrades gracefully and says why, without
> affecting any core feature.

---

## Regenerate / extend

```bash
cd _scripts

python3 fetch_art.py                  # fetch images for movements that lack them
python3 fetch_art.py impressionism    # one movement only
python3 fetch_art.py --per 12         # 12 images per movement
python3 build_vault.py                # regenerate every note from the mv_*.py data
python3 make_links.py                 # regenerate external search deep links
```

### Adding a movement

1. Add an entry to the right `_scripts/mv_*.py` file
2. Add filter keywords to **`ARTIST_KEYS` in the same file** ← **required, or you'll pull in unrelated works**
3. `python3 fetch_art.py <slug>` then `python3 build_vault.py`

| Data file | Category |
|---|---|
| `mv_core.py` | the original 18 core movements |
| `mv_west.py` | Western Classical & Modern |
| `mv_asia.py` / `mv_asia2.py` | East Asia · South Asia · Islam |
| `mv_modern.py` / `mv_gaps.py` | Modernism & Post-war |
| `mv_contemporary.py` | Avant-Garde · Contemporary · Postmodern |
| `mv_visual.py` | Digital · Subculture · Photography |
| `mv_photo.py` | Photography & Image |

---

## Tool inventory

What each script in `_scripts/` does. Unless marked **optional**, all of them
need only Python 3 + Pillow.

### Entry points

| Script | What it does |
|---|---|
| `artvault.py` | Main query interface: `categories` `search` `layers` `show` `palette` `related` `compose` |
| `mcp_server.py` | Same capabilities exposed as an MCP server for Claude Desktop / Cursor |

### Sources & generation

| Script | What it does |
|---|---|
| `movements.py` | Aggregates all 141 movement definitions — the single source of truth |
| `mv_*.py` | Movement cards and filter keywords (8 files, split by category) |
| `providers.py` | Four CC0 source adapters + three-layer filtering (AI images / flat works / artist match) |
| `fetch_art.py` | Image fetching: round-robin across sources, two-layer filtering, `--refresh` clears orphaned files |
| `build_vault.py` | **Generates** the Obsidian notes / README / LICENSE / .gitignore |
| `make_links.py` | Generates external search deep links |
| `keyword_map.py` | Generates the keyword map |

### Image analysis

| Script | What it does |
|---|---|
| `image_analysis.py` | Seven objective dimensions: luminance / contrast / colour / harmony / composition / texture / line. Pure Pillow |
| `image_analysis_ext.py` | **Optional**: face framing / Hough lines / spectral-residual saliency. Needs numpy + opencv, skipped automatically if absent |
| `clip_embed.py` | **Optional**: CLIP image/text embeddings (ONNX, no PyTorch). Run `download` once for the model |
| `clip_match.py` | **Optional**: image-to-movement matching with CLIP (zero-shot + fusion) — the most accurate of the three routes |
| `artvault_vision.py` | **Optional**: macOS Vision semantic search (search by image / near-duplicates / similar movements) |
| `ingest_inbox.py` | Processes the `pinterest/` inbox, including the dimensions above in its scan |
| `verify_vault.py` | **Acceptance checks**: broken links / duplicate names / AI images / frontmatter / near-duplicates / licences / orphans |
| `github_setup.py` | Push, set as Template, set topics/description in one go (token never appears in argv) |
| `movement_fingerprint.py` | Movement fingerprints from objective dimensions for image-to-movement matching (explainable, but measurably worse than Vision) |
| `video_prompt.py` | Generates two Chinese video-prompt blocks per movement (Seedance 2.5 five-part + MiniMax H3 natural language) |
| `scan_local.py` | **Scans your own image folders into the vault**: measurement + CLIP suggestions + dedupe → review list → files into `15-我的图库/` |
| `reverse_prompt.py` | **Composes the reverse-engineering card**: measurements + movement match + 7 layers + video prompts, shared by all three entry points |
| `pinterest_grab.py` / `pinterest_export.py` | Pinterest scraping and export (local use only, images are **not** committed) |

### Two conventions that are easy to miss

1. **Change the template, not the output.**
   `10-流派/*.md`, `00-导航/*.md` and `README.md` are all generated by
   `build_vault.py`; editing them directly loses the change on the next rebuild
   (this tool inventory itself lives in the template).
2. **`20-我的提示词/` is yours.** Scripts read it but never overwrite it.

---

## Three principles

1. **Better fewer than wrong.**
   Filtering deliberately does *not* have a "top up with whatever's available" fallback -
   if a movement yields one image, it gets one image.
   > The worst thing for a reference library isn't too few images, it's wrong ones.
   > Wrong references corrupt your instincts, and you won't notice.

2. **Lighting matters more than style keywords.**
   If you can only tune one layer, tune lighting.

3. **Don't invent movement terminology from memory.**
   LLM recall on art movements is unreliable and blurs related schools together.
   Use the concrete terms in the library.

---

## Image sources

All images come from public-domain / CC0 open sources (Cleveland, Art Institute of Chicago, The Met, Wikimedia Commons), verified entry by entry.
Free to use and redistribute. Every work is annotated with its source and license link.

**Code** MIT ｜ **Notes** CC BY 4.0

---

<div align="center">

If this is useful, a star is appreciated - PRs adding more movements are welcome

</div>
