---

name: article-illustration-planner
description: Analyze an article, choose the most valuable illustration positions, design what each illustration should communicate, and generate image prompts using a selected style from the hand-drawn style library. Supports both preserving the original article and selectively replacing or simplifying text with visual expression.
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Article Illustration Planner

Turn an article into a coherent visual-illustration plan.

The user provides:

* an article or substantial article draft;
* a hand-drawn style number from the installed style library.

The Skill decides:

* whether the article actually benefits from illustrations;
* where illustrations add the most value;
* how many illustrations are appropriate;
* what each image should communicate;
* whether an image should supplement, explain, replace, or reorganize part of the text;
* how to express each illustration in the selected visual style.

Do not mechanically illustrate every paragraph.

Do not distribute images at fixed intervals.

Do not force a predetermined number of illustrations.

The primary task is **visual editorial judgment**, not filling empty spaces with pictures.

---

# Core Principle

First determine:

> What does this article need visually?

Only then determine:

> What should each image contain?

The selected style number controls **how the image is drawn**.

It must not determine **what the image is about**.

Separate these two decisions:

1. visual communication strategy;
2. visual style.

---

# Default Behavior

Default to **Preserve mode**.

In Preserve mode:

* do not rewrite the article;
* do not delete article content;
* identify suitable insertion points;
* design illustrations that supplement the existing text.

Only modify, shorten, replace, or reorganize article text when the user explicitly requests or accepts **Visual Rewrite mode**.

Do not generate images unless the user explicitly asks to generate, render, preview, or produce the images.

The normal first response is an illustration plan plus generation prompts.

---

# Inputs

Required:

1. Article content.
2. Style number.

Resolve the style number from the current installed hand-drawn style index. Do not hard-code the maximum style number into this Skill.

Optional user constraints may include:

* publishing platform;
* desired illustration density;
* aspect ratio;
* whether a cover image is needed;
* whether text may be modified;
* whether text may appear inside images;
* target audience;
* any subjects, symbols, visual elements, or content the user wants to avoid.

Do not require optional parameters when the article itself provides enough information.

Infer sensible decisions from the article whenever possible.

---

# Modes

## Preserve Mode

Default mode.

Keep the article unchanged.

Illustrations may:

* establish atmosphere;
* create visual pauses;
* reinforce an important idea;
* make an abstract idea concrete;
* explain a difficult concept;
* visualize a process or relationship;
* create a visual transition;
* strengthen the ending.

The images supplement the article rather than replacing it.

---

## Visual Rewrite Mode

Use only when requested or clearly approved by the user.

The Skill may selectively:

* shorten repetitive passages;
* remove text that can be communicated more effectively through an image;
* convert explanatory prose into a visual relationship;
* turn long comparisons into visual comparisons;
* convert processes into visual sequences;
* reorganize a small section around an illustration.

Preserve the author's meaning, tone, and argument.

Do not rewrite the whole article simply because rewriting is allowed.

Prefer the smallest textual intervention that creates a meaningful improvement.

Never remove information whose precision is important and difficult to preserve visually.

Examples include:

* exact definitions;
* numbers;
* dates;
* legal or technical wording;
* important qualifications;
* source attribution;
* factual distinctions;
* conclusions that could become ambiguous when converted into imagery.

---

# Article Understanding

Before selecting images, understand the article as a whole.

Internally identify:

* central idea;
* article type;
* major sections;
* argument or narrative progression;
* information-density changes;
* emotional changes;
* conceptual difficulty;
* places where prose becomes repetitive;
* places where a visual could communicate something words are currently carrying inefficiently.

Do not expose lengthy internal analysis unless the user asks for it.

The visible output should focus on useful editorial decisions.

---

# Article Types

Do not require the user to classify the article.

Infer its dominant visual needs.

Possible tendencies include, but are not limited to:

### Reflective / philosophical

Usually benefits from:

* metaphor;
* symbolic scenes;
* emotional transitions;
* visual pauses;
* restrained narrative moments;
* visual echoes of the article's central idea.

Avoid merely drawing a literal person who is "thinking", "sad", or "happy" when a stronger visual metaphor is possible.

### Narrative / personal essay

Usually benefits from:

* key moments;
* environmental storytelling;
* objects with narrative meaning;
* changes in relationship, place, time, or emotional state.

### Explanatory / educational

Usually benefits from:

* concept visualization;
* analogy;
* causal relationships;
* processes;
* systems;
* hierarchy;
* comparison;
* transformation over time.

Do not reduce every educational illustration to a conventional infographic.

A hand-drawn explanatory illustration may combine objects, characters, spatial relationships, labels, diagrams, and metaphor when that communicates the idea more clearly.

### Argumentative / analytical

Usually benefits from:

* contrasts;
* competing forces;
* cause and effect;
* hidden relationships;
* structural models;
* before-and-after states;
* visual synthesis of a key argument.

### Mixed articles

Use different illustration functions when appropriate.

Do not force every image in an article to perform the same job.

---

# Illustration Functions

For every proposed image, decide its primary purpose.

Possible functions include:

* `opening-visual` — establishes the article's visual premise;
* `metaphor` — translates an abstract idea into a visual situation;
* `narrative-scene` — depicts a meaningful moment or situation;
* `concept-explanation` — makes a difficult concept easier to understand;
* `relationship` — visualizes relationships among ideas or entities;
* `process` — visualizes sequence, causality, or transformation;
* `comparison` — contrasts two or more states or ideas;
* `visual-pause` — creates rhythm and emotional breathing room;
* `transition` — bridges two sections;
* `summary` — condenses a section or conclusion visually;
* `text-replacement` — carries information that would otherwise require substantial prose.

These are reasoning categories, not rigid templates.

Do not force the final image into a conventional diagram solely because its function is explanatory.

---

# Image Type

For every proposed image, choose one concise image-type keyword. The type tells the image model what kind of picture to create; it does not replace the illustration function, visual idea, or selected drawing style.

Use one of these fixed values:

* `editorial illustration` — a broad, article-led visual that establishes or reinforces an argument;
* `conceptual diagram` — an explanatory relationship, system, or abstraction;
* `process diagram` — a sequence, causal chain, cycle, or transformation;
* `comparison diagram` — a contrast between states, groups, or outcomes;
* `narrative scene` — a concrete, meaningful moment or situation;
* `metaphorical illustration` — a symbolic visual situation for an abstract or emotional idea.

Choose the type from the illustration's purpose and visual approach. Do not ask the user to select it unless they explicitly want to override it. If the user supplies an image type for a specific illustration, preserve that value when it is one of the fixed values.

Use the same selected value in the illustration plan and both copyable prompts. Do not add multiple type labels to one image or invent near-synonyms.

---

# Selecting Illustration Positions

Choose illustration positions according to editorial value.

Good candidates often occur where:

* the article introduces its central idea;
* an abstract idea becomes important;
* the reader must understand a relationship;
* explanation becomes text-heavy;
* a major emotional or argumentative turn occurs;
* the article shifts from one conceptual section to another;
* a concrete scene could make an idea memorable;
* the ending benefits from visual resonance.

Do not choose positions merely because a paragraph is long.

Do not insert an image when it would interrupt a strong reading rhythm.

It is acceptable to recommend very few illustrations.

It is also acceptable to recommend no illustration for a section.

The number of images should emerge from the article.

---

# Visual Compression

When Visual Rewrite mode is enabled, look for opportunities where visual expression can reduce textual load.

A candidate is strong when the image can preserve the essential meaning while requiring substantially less prose.

Good candidates include:

* relationships;
* processes;
* categories;
* cycles;
* comparisons;
* spatial structures;
* recurring patterns;
* concrete analogies;
* emotional metaphors.

Weak candidates include information whose value depends on exact wording or precise factual details.

When proposing visual replacement, explicitly identify:

1. what text can be shortened or removed;
2. what information the image must preserve;
3. what text, if any, must remain beside the image.

---

# Designing Each Illustration

For each selected position, determine the image from the article's meaning rather than from generic visual tropes.

Prefer a clear visual idea over a long list of objects.

A strong illustration should usually have:

* one dominant visual proposition;
* a clear relationship to the surrounding text;
* enough specificity to communicate the intended idea;
* enough openness for the image model to make aesthetic decisions.

Do not over-specify:

* exact object placement;
* exact camera position;
* exhaustive prop lists;
* decorative details;
* lighting;
* composition;
* rendering quality;

unless they are necessary to communicate the article's idea or the user explicitly requests them.

Allow the image model room to solve the visual problem.

---

# Metaphor Design

For reflective, philosophical, emotional, or abstract writing, avoid literal illustration when a stronger metaphor is available.

A metaphor should:

* express the underlying relationship or tension;
* remain understandable without explaining every detail;
* add meaning rather than merely decorate;
* avoid clichés when a fresher visual situation is available.

Do not automatically reuse common motifs such as:

* crossroads;
* ladders;
* cages;
* cliffs;
* mirrors;
* broken clocks;
* lone figures staring into the distance.

They may be used when genuinely appropriate, but they are not default solutions.

Generate the metaphor from the specific article.

---

# Knowledge Illustration

For knowledge-oriented articles, optimize for understanding rather than decoration.

Ask:

> What does the reader need to see in order to understand this faster or more deeply?

Possible visual structures include:

* objects interacting;
* spatial relationships;
* visual analogy;
* transformation;
* layers;
* sequences;
* branching relationships;
* opposing states;
* nested systems;
* annotated scenes;
* illustrative diagrams.

Do not invent factual relationships that are not supported by the article.

If the source article is ambiguous, preserve that ambiguity rather than fabricating precision.

Any numbers, labels, names, or factual claims placed inside an image must come from the article or other user-provided material unless the user explicitly asks for external research.

---

# Style Integration

After the visual concept has been decided, resolve the selected style number through the installed hand-drawn style library.

Reuse the current style library's canonical:

* style number;
* generation style name;
* reference author/style name;
* model capability / reference-image policy when image generation is requested.

Do not duplicate the full style library inside this Skill.

Do not independently invent visual traits for an indexed style.

When generation is requested, defer style-resolution behavior to the hand-drawn style package whenever possible.

The article illustration Skill determines:

> what to communicate.

The hand-drawn style Skill determines:

> how that selected style should be invoked.

---

# Prompt Writing

Each image prompt should be concise enough to leave meaningful creative freedom to the image model.

The prompt should primarily contain:

1. selected style identity;
2. image type;
3. the visual idea;
4. necessary subjects and relationships;
5. essential factual content;
6. user-specified constraints.

Write image type as a standalone field near the beginning of every copyable prompt:

* Chinese prompt: `图片类型：{image_type}。`
* English prompt: `Image type: {image_type}.`

Place this field before the theme or visual idea. In graphic-text mode, it must appear before `主题：` / `Theme:` and must not alter the fixed suffix required by the hand-drawn style package.

Do not automatically add:

* generic quality terms;
* elaborate camera instructions;
* excessive rendering adjectives;
* long negative prompts;
* unnecessary composition rules.

For philosophical articles, emphasize the visual metaphor or situation.

For knowledge articles, emphasize the relationship the image needs to explain.

Do not simply paste the surrounding paragraph into the image prompt.

Translate meaning into visual information.

---

# Text Inside Images

Use text inside an illustration only when it materially improves comprehension or when requested by the user.

Prefer little or no text for:

* emotional illustration;
* metaphorical illustration;
* narrative scenes.

Text can be useful for:

* labels;
* simple comparison;
* process stages;
* key relationships;
* short conceptual annotations.

Do not turn every illustration into a poster.

Do not reproduce long article passages inside images.

---

# Output

Start with a concise overall recommendation.

Include:

* inferred article type;
* visual strategy;
* recommended number of illustrations;
* whether any section would benefit from visual replacement.

Then provide each illustration in reading order.

For each image use:

### Illustration N

**Insert after:**
Identify the location using the nearest heading or a short recognizable excerpt from the article.

**Purpose:**
Explain what this image contributes to the reading experience.

**图片类型：**
One selected value from the fixed image-type list.

**Visual approach:**
Describe the central visual idea in a few sentences.

**Relationship to text:**
One of:

* supplements text;
* explains text;
* visually summarizes text;
* replaces part of text.

If text modification is proposed, identify the exact passage and provide the proposed revised text.

**Style:**
Selected style number and resolved style name.

**Image prompt:**
Provide generation-ready Chinese and English prompts. Each prompt must include the same image-type field before its theme or visual idea.

Do not include unnecessary implementation commentary between illustrations.

---

# Modified Article

In Preserve mode, do not reproduce the entire article unless the user requests it.

In Visual Rewrite mode, after the illustration plan, provide a revised article only when useful or explicitly requested.

When returning a revised article:

* preserve the author's voice where possible;
* mark illustration insertion positions clearly;
* integrate the visual plan into the reading flow;
* do not rewrite unaffected passages unnecessarily.

---

# Cover Image

Do not assume every article needs a cover image.

Recommend one when it adds value for the publishing context or gives the article a useful visual premise.

A cover image may communicate the article as a whole and does not need to literally summarize every section.

---

# Interaction

If the article and style number are sufficient, proceed directly.

Do not ask the user to choose:

* article type;
* number of images;
* illustration categories;
* metaphor style;
* information-visualization type;

when these can be inferred from the article.

Ask a question only when missing information materially prevents a good result.

Otherwise use editorial judgment.

---

# Image Generation

The default output is the plan and prompts.

Only generate images after explicit user instruction.

The user may request:

* all images;
* a specific illustration;
* revisions to one visual concept;
* an alternate concept;
* different illustration density.

When generating multiple article illustrations, maintain a coherent visual identity while allowing composition and subject matter to vary according to the role of each image.

Do not make all illustrations visually repetitive merely for consistency.

---

# Design Philosophy

This Skill should remain intentionally lightweight.

Prefer:

* judgment over rules;
* meaning over templates;
* article-specific visual thinking over generic motifs;
* minimal input over configuration forms;
* concise prompts over exhaustive specifications;
* AI reasoning over manually encoded decision trees.

Rules in this Skill exist mainly to prevent poor default behavior.

They must not replace the model's ability to read, interpret, and visually rethink an article.
