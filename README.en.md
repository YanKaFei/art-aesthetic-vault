<div align="center">

<img src="99-attachments/readme/hero.jpg" width="100%" alt="Art movements, hand-drawn styles and film stills across the four axes">

# Art Aesthetic Style Library

**Visual style, decomposed into prompt layers you can actually call**

Movements · Hand-drawn · Directors · Camera moves - four axes, one structure

[![DeepSeek Harness](https://img.shields.io/badge/DeepSeek%20Harness-dsh--plugin-4D6BFE?style=flat-square)](https://github.com/deepseek-ai/deepseek-harness)
[![Agent Skill](https://img.shields.io/badge/Agent-Skill-7C3AED?style=flat-square)](.repo/skill)
[![License](https://img.shields.io/github/license/YanKaFei/art-aesthetic-vault?style=flat-square)](LICENSE)

`421 movements` · `274 hand-drawn styles` · `100 films` · `157 shot recipes` · `686 notes` · `746 images`

[中文](README.md) ｜ [日本語](README.ja.md) ｜ [Français](README.fr.md) ｜ **English**

</div>

---

## What this is

Most people collect style references by saving images. You end up with a few hundred
of them and no idea what to look at or how to describe it. Images are dead weight.

This vault does something else: **it decomposes each visual language into seven
independently replaceable layers.**

<img src="99-attachments/readme/layers.png" width="100%" alt="Seven layers: style / lighting / color / composition / medium / mood / camera">

Once it is in layers, you can put the lighting of image A onto the subject of image B.
**That is the actual point of a reference library.**

```bash
python3 artvault.py compose \
  "a bounty hunter in a rainy neon street, baroque lighting, cyberpunk framing" \
  --subject "a female bounty hunter in a wet neon alley"
```

It reads the intent behind each phrase ("baroque" followed by "lighting" gets the
baroque lighting layer), then emits layered positive prompts, negative prompts,
a palette, a video layer, and a **conflict-resolution record**.

> **Same subject, every layer swappable.** That is the difference between this and a
> pile of style keywords.

---

## Four axes

All four axes share the same card structure and the same seven-layer vocabulary,
so you can mix across axes: a film's lighting + a movement's palette + a
hand-drawn medium.

| | Axis · scale | What it answers |
|---|---|---|
| <img src="99-attachments/readme/axis-1-movements.jpg" width="300" alt="Art movements"> | **Art movements · 421**<br>(7 categories) | Byzantine to Y2K, ukiyo-e to cyberpunk. One card per movement: six-axis visual breakdown + seven prompt layers + six-colour palette + targeted negatives + video layer<br>`python3 artvault.py layers baroque` |
| <img src="99-attachments/readme/axis-2-handraw.jpg" width="300" alt="Hand-drawn styles"> | **Hand-drawn styles · 274**<br>(groups A-H) | Storybooks, editorial cartoons, contemporary illustration, guofeng... from [handraw-style](https://github.com/yang0/handraw-style) (**MIT**), merged in whole. Cards are named in Chinese, with the upstream number kept as an alias<br>`python3 artvault.py layers 极端比例弯曲绘本` |
| <img src="99-attachments/readme/axis-3-films.jpg" width="300" alt="Directors and films"> | **Directors & films · 100**<br>(44 directors) | Not just "what it looks like" but "who shot it and how". Organised director then film: representative frames + six-axis breakdown + seven prompt layers + palette + video layer, plus **6142 external still links** (indexed, never rehosted)<br>`python3 artvault.py film show dune` |
| <img src="99-attachments/readme/axis-4-shots.jpg" width="300" alt="Shot recipes"> | **Shot recipes · 157**<br>(10 categories) | The first three axes answer "what does it look like"; this one answers "**how do I actually make that move**". Frames, easing and amplitude as parameter tables, with known pitfalls. From [video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft) (**Apache-2.0** - this vault only categorises and formats them)<br>`python3 artvault.py shots show crash-zoom-punch` |

> ⚠ **Shot cards have no colour or lighting fields, deliberately.** They talk about
> frame counts and easing (`zoom 6f ease-in, 1 to 2.6`); forcing them into the
> seven layers would mean inventing content. So they carry their own four fields and
> **stay out of `compose` layer resolution** - a test guards that boundary.

---

## At a glance

<img src="99-attachments/readme/gallery.jpg" width="100%" alt="Sample movements, hand-drawn styles and films in this vault">

| | |
|---|---|
| **Movement cards** | **421**, in 7 categories. Each has a 6-axis visual breakdown, 7 prompt layers, a 6-color palette, a video layer, and known failure modes |
| **Images** | **746** (167 MB) = **452** public-domain museum images + **294** handraw-style numbered reference sheets (MIT); covering 359 movements |
| **Hand-drawn card names** | **274 / 274** named (249 derived word-for-word from `traits`; 25 back-translated from the English generation name where `traits` is empty) |
| **Guides & methodology** | 15 notes (overview, keyword atlas, the 7-layer method, video structure, palette index...) |
| **Keyword atlas** | The **4 most-confused concept groups**, **46 synonyms** in total - search any of them and land on the same card |
| **Film style cards** | **100** (44 directors), organised director then film: still index + six-axis breakdown + seven prompt layers + palette + video layer, plus **6142 external still links** (indexed, never rehosted) |
| **Shot recipe cards** | **157** (10 categories): camera moves and motion effects with parameter tables (frames/easing/amplitude) and known pitfalls. From [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft), **Apache-2.0 - this vault only categorises and formats them** |
| **Note templates** | 3 |
| **Scripts** | 65 - fetch, generate, search, compose, MCP server |

> **62 movements are "prompt-only cards."** Abstract Expressionism, Pop Art,
> Minimalism, Conceptual Art, Cyberpunk, Vaporwave - freely distributable images for
> these essentially do not exist. Their visual language and seven layers are broken
> down exactly as usual; they simply carry no images. That is a deliberate design
> decision, not a gap.

---

## How to use it

### 1. Read it as an Obsidian vault

Open this folder in Obsidian. A good order to walk in:

1. `00-guides/提示词拆解方法.md` - **start here** to understand the seven layers
2. `00-guides/流派总览.md` - the master index of every movement
3. `10-movements/` - pick a movement you like and read its full breakdown
4. `00-guides/关键词图谱.md` - look up any unfamiliar style term later

### 2. Let an AI call it

This is not only Markdown for humans; there is a **machine-facing interface**:

```bash
cd .repo

python3 artvault.py categories              # the 7 categories
python3 artvault.py search "neon rain"      # fuzzy search, Chinese or English
python3 artvault.py search "oppressive but gorgeous light" --semantic
python3 artvault.py layers baroque          # just the seven layers (cheapest)
python3 artvault.py show ukiyo-e            # the full card
python3 artvault.py palette cyberpunk       # the six-colour palette
python3 artvault.py related cubism          # neighbouring movements

python3 artvault.py film list               # 100 films
python3 artvault.py shots search "crash zoom punch"

python3 artvault.py --json layers baroque   # machine readable
```

**Composition is the core capability**:

```bash
# natural language, layered automatically
python3 artvault.py compose "a bounty hunter in rainy neon, baroque lighting" \
  --subject "a bounty hunter"

# explicit, mixing eras
python3 artvault.py compose --style ukiyo-e --lighting baroque \
  --color vaporwave --composition precisionism --subject "a lone samurai"

# across axes: a film's lighting + a movement's palette
python3 artvault.py compose --lighting villeneuve-dune --color baroque \
  --subject "a lone figure on a dune"
```

It **resolves layer conflicts automatically**. When you mix movements, their negative
prompts contradict each other - ukiyo-e bans `cast shadows`, baroque lighting demands
`deep crushed shadows`; precisionism bans `people` while your subject *is* a person.
**The model does not error**; you just get "mysteriously bad images", which is
extremely hard to debug. So conflicting negatives are **removed from the negative
prompt** and listed one by one under "auto-resolved conflicts", saying what was
dropped and what it yielded to. The rule in one line: **positives are intent,
negatives are guardrails, and guardrails yield to intent.** Add `--keep-conflicts`
to see the raw union and judge for yourself.

### 3. Install it as an AI skill (recommended)

The repo ships two skills. Once installed, **any skill-aware AI assistant** will
consult this vault for visual/aesthetic tasks instead of inventing movement
terminology from memory.

```bash
cd .repo/skill && ./install.sh
```

| skill | Does what | Triggers when |
|---|---|---|
| `art-aesthetic-vault` | **Use** the vault: search movements, pull seven layers, compose across movements | You ask "what style should this character be?" |
| `build-art-aesthetic-vault` | **Build** a vault: start one from scratch | You say "I want a library like this" |

> [!note] Why neither skill bundles the data
> Both are **symlinks** into this repo - there is exactly one copy of the data.
> If `mv_*.py` (the movement definitions) were packaged into the skill, there would
> be two copies and they would inevitably diverge. We tested this: the packaged
> version had 4 files out of sync with the repo, and vaults built from it had the
> wrong categories.

It creates symlinks in every skill directory it can find:

| Directory | Read by |
|---|---|
| `~/.agents/skills/` | DSH / Codex / general convention |
| `~/.claude/skills/` | Claude Code |
| `~/.codex/skills/` | Codex |

**Why symlinks**: the skill resolves its own real location with `pwd -P` and infers
the repo root from it - **wherever the repo lives, and however you move it, it is
found automatically**, with no configuration.

```bash
.repo/skill/install.sh --copy        # copy instead (must reinstall if the repo moves)
.repo/skill/install.sh --uninstall
bash .repo/skill/locate.sh           # locate the repo manually (for debugging)
```

Skills take effect in a **newly started AI session**.

### 4. Hook it up over MCP (Claude Desktop / Cursor)

```json
{
  "mcpServers": {
    "artvault": {
      "command": "python3",
      "args": ["<absolute path to this repo>/.repo/mcp_server.py"]
    }
  }
}
```

16 tools are exposed: `search_movements` `get_movement` `get_layers` `compose_prompt`
`get_palette` `find_related` `list_categories` `analyze_image` `match_movement`
`get_video_prompt`, plus `search_films` `get_film` `get_film_layers` `get_film_stills`
for the film library and `search_shots` `get_shot` for the shot library.
The last few need Pillow / a CLIP model; when unavailable they explain why, and the
first seven are unaffected.

---

## Why it is different

### 1. Not an image pack - a composable structure

An image pack gives you "what this feels like"; this gives you "how to produce that
feeling". Every layer can be lifted out on its own: keep the style layer, swap the
subject, and you have a style-transfer template.

### 2. Lighting is pulled out as its own layer

Most people write prompts as one blended lump and tune by trial and error. This vault
states it plainly: **lighting affects the final texture more than the style words do.**
Each movement's lighting layer is a separate block you can move onto another subject.

### 3. Every axis has targeted negatives

Aimed at **this movement's** typical failure mode, not a generic negative list:

- Impressionism -> `black shadows, smooth blending, photorealistic`
- Renaissance -> `visible brushstrokes, impasto` (AI adds impasto to oils by default)
- Ukiyo-e -> `3d shading, cast shadows, gradient` (AI adds volume by default)

**Note that different movements' negatives often contradict each other** - which is
exactly why mixing fights, and exactly what this vault manages for you.

### 4. An AI can use it, not just look at it

LLMs remember art movements fuzzily and routinely confuse Art Nouveau with Art Deco,
or Barbizon with Impressionism. This vault pins down the concrete terminology so an
AI calling it will not make things up.

### 5. The terminology is pinned, not invented

The keyword atlas picks the **4 most-confused concept groups** - avant-garde,
contemporary, postmodern, surreal. Each gets a definition, several "what it is not"
boundaries, and **46 synonyms**; searching any of them lands on the same card.

### 6. An image you already have can become a video prompt

The video prompts on the cards are **generic** - the subject line is a placeholder.
But what you usually want is "I have this image, make it move":

```bash
python3 i2v_prompt.py your-image.jpg --slug baroque
```

Shot size, position in frame, internal motion direction, whether the light should
move, whether the camera pushes or pans - all derived from **objective measurements
of that image** (face-based shot size / saliency centre / line direction / detail
density / light-dark structure), with a "derivation basis" sheet for you to check.
The output still leaves "who, doing what - add one line yourself": only the person
looking at the image knows that, and the script will not invent it.

### 7. The numbers are computed, not hard-coded

Every "how much is in this vault" number in the READMEs is computed by
`publish_stats()` against the **published view** (what git tracks, not what happens to
be on the author's machine) and then checked line by line by `verify_vault.py`.
The only thing a hard-coded number ever does is become wrong one day - this vault has
been burned by that, so the lock is in place.

---

## Three principles

1. **Rather less than wrong.**
   Curation deliberately refuses "broaden it a bit" - if a movement has one image,
   it has one image. The real danger for a reference library is not too few images
   but wrong ones: a wrong reference contaminates your intuition and you never find out.

2. **Lighting matters more than style words.**
   If you can only tune one layer, tune lighting.

3. **Do not invent movement terminology from memory.**
   LLM memory of art movements is fuzzy and conflates neighbouring schools.
   Trust the concrete terminology in the vault.

---

<details>
<summary><b>Expand the full skill tree (421 movements / 7 categories)</b></summary>

Art Aesthetic Style Library
│
├─ Western Classical & Modern · 48
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
│  ├─ American & Modern Schools
│  │  ├ Hudson River School . Luminism . Tonalism
│  │  ├ Ashcan School . American Realism . Regionalism
│  │  ├ Precisionism . Social Realism . Socialist Realism
│  │  ├ Muralism . Magic Realism . Metaphysical Art
│  │  ├ Neo-Romanticism . Naïve Art (Primitivism) . Classical Realism
│  │  └ Kitsch . New Objectivity
│  └─ Others
│      └ Biedermeier
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
├─ Modernism & Post-war · 24
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
│      └ Superflat . Neo-Expressionism . Cubo-Futurism
├─ Digital · Subculture · Photography · 25
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
│  ├─ Cinematic
│  │  └ Film Noir
│  └─ Others
│      └ Fantasy Art
├─ Avant-Garde · Contemporary · Postmodern · 23
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
│      ├ Neo-Geo . Post-Minimalism . Spatialism
│      └ Art Informel . Tachisme . Lyrical Abstraction
├─ Photography & Image · 6
│  ├─ Two Traditions
│  │  └ Pictorialism . Straight Photography
│  ├─ Social & Street
│  │  └ Documentary Photography . Street Photography
│  └─ Conceptual & Fashion
│      └ Surrealist Photography . Fashion Editorial
└─ Hand-drawn Illustration Styles · 274
   ├─ International Editorial Cartoon / Humour
   │  └ 35 entries (see the category index)
   ├─ International Picture Book / Narrative
   │  ├ Loose Ink-and-Wash Storybook . Nordic Fine-Line Whimsy . Busy Anthropomorphic Everyday World
   │  ├ Warm Vintage Line-and-Wash . Crosshatched Wild Storybook . Bendy Absurd Storybook
   │  ├ Naturalist Watercolor Animal Storybook . Classic Pen-and-Light-Wash Storybook . Quirky Ink-and-Watercolor Tale
   │  ├ Minimal Poetic Picturebook Doodle . Bold Geometric Picturebook . Muted Deadpan Picturebook
   │  ├ Folk-Line Decorative Storybook . Dreamlike Surreal Storybook . Layered Vintage Storybook Collage
   │  ├ Expressive Character Sketch Cartoon . Dreamlike Clean-Line Sci-Fi Figure . European Clear-Line Adventure Figure
   │  └ Geometric European Clear-Line Figure
   ├─ Modern Graphic / Stylised Figures
   │  └ 28 entries (see the category index)
   ├─ Japanese Authors / Contemporary Illustration
   │  └ 41 entries (see the category index)
   ├─ Chinese Authors / Contemporary Illustration
   │  └ 31 entries (see the category index)
   ├─ General Web / Medium / Regional
   │  └ 46 entries (see the category index)
   ├─ New Additions / Chinese Contemporary
   │  ├ 可爱萌系插画风 . 诗意青春插画风 . 唯美漫画插画风
   │  ├ 水墨新国风插画 . 魔性幽默漫画风 . 都市生活漫画风
   │  ├ 极简温暖叙事风 . 东方美学商业插画 . 童趣水彩绘本风
   │  ├ 东方奇幻绘本风 . 清新文艺插画风 . 复古潮流插画风
   │  ├ 可爱萌系插画风 . 国风幻想插画风 . 治愈生活插画风
   │  └ 时尚女性插画风
   └─ Others
       └ 58 entries (see the category index)

</details>

---

## Contributors & sources

This vault exists because a number of people **chose to open their work up**. None of
the items below is a passing "we looked at it" - each was **taken in whole and
re-cut into the same card structure**:

| Source | What it contributed | License |
|---|---|---|
| [yang0/handraw-style](https://github.com/yang0/handraw-style) | **274 hand-drawn styles** and their numbered reference sheets, forming category 7 | **MIT** |
| [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft) | **157 shot recipe cards** (10 categories); this vault only categorises and formats them | **Apache-2.0** |
| [film-grab.com](https://film-grab.com/) | The film still index; the representative frames embedded in cards remain the **copyright of the respective rights holders** | Site states: *images are not permitted for commercial use*. Personal study reference only |
| [Tate art terms](https://www.tate.org.uk/art/art-terms) | The glossary pages cited in each movement card's sources section - the seven layers trace back to authoritative definitions | Term text is **copyright Tate**; this vault **cites the source only** |
| [Cleveland Museum of Art](https://openaccess-api.clevelandart.org) · [Art Institute of Chicago](https://api.artic.edu/docs/) · [The Met](https://collectionapi.metmuseum.org) · [Wikimedia Commons](https://commons.wikimedia.org) | **452 public-domain museum images** | **CC0 / public domain** |

**Three boundaries worth stating plainly**:

1. **The shot cards are not original to this vault.** Copyright in those
   157 technique descriptions belongs to the upstream project (Apache-2.0).
   This vault only categorises and formats them, and each card carries the upstream
   path and commit. The upstream project states that the motion techniques were
   studied from publicly released works, that **every implementation was rewritten
   from scratch** with no original footage, and that "publicly released" is
   **not** the same as "licensed". Do not use these cards to reproduce the
   recognisable overall audiovisual presentation of a specific work.
2. **Film stills remain the copyright of the respective rights holders.** The
   representative frames embedded in cards are for **personal study reference only**;
   film-grab states they may not be used commercially. Obtain permission before
   redistributing or using commercially.
3. **"Referenced artist / style names" are index labels** - not descriptions of the
   people themselves, and not an instruction to imitate. The numbered reference
   sheets are used for style only: do not carry over their subjects, compositions
   or text.

This vault's own parts (the seven-layer breakdown, card structure, CLI / MCP,
retrieval and composition logic) are released under MIT.

---

## License

- **Code and card text**: [MIT](LICENSE)
- **Public-domain images**: CC0 / public domain; source and license are stated in each card's sources section
- **handraw-style numbered reference sheets**: MIT (upstream)
- **Shot recipe cards**: Apache-2.0 (upstream); this vault only categorises and formats them
- **Film stills**: copyright of the respective rights holders; personal study reference only

---

<div align="center">

If this is useful, a star is appreciated - PRs adding more movements are welcome

</div>
