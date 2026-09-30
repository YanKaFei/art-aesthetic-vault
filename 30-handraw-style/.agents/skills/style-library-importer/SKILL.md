---
name: style-library-importer
description: Add a named or text-defined visual style to the numbered hand-drawn style library, generating a square representative image when none is supplied. Do not use for image-only Tweet imports.
---

# Text-Defined Style Library Importer

Use this Skill when the user wants to add a visual style to the local hand-drawn style library with a style name, visual traits, or both. It is separate from `tweet-style-importer`: an image-only request belongs to the Tweet workflow and must not receive a new number here.

## Interpret the input

- **Name only:** keep the supplied name as the style label, do not invent or store visual traits, and register `name_activation=strong`, `traits_activation=none` for `gpt-image-2`.
- **Name plus traits:** preserve the name, retain only positive concrete visual traits, remove negative clauses such as `避免`、`不要`、`不准`、`禁止` or `无写实纹理`, and register `name_activation=weak`, `traits_activation=strong`.
- **Traits only:** invent a readable Chinese style label and a concise English generation name, retain only positive concrete visual traits, and register `name_activation=weak`, `traits_activation=strong`.
- **Image only:** do not change the library. Explain that image-only imports are handled by `tweet-style-importer`.

For every text-defined style, `gpt-image-2` must use its configured text activation and must not receive a reference image. Unknown models retain the library's existing image fallback behavior.

## Representative image

If the user provides an image alongside textual input, use it directly as the representative source image; do not generate another one.

If no image is provided, generate exactly one original 1:1 representative image with `gpt-image-2`. Select a simple neutral subject and setting that make the declared style legible. Use the supplied name and, when present, the filtered positive traits; do not reuse subjects, actions, scenes, compositions, or stories from existing library entries. Generate one image, not a contact sheet.

## Import

After a representative image is available, run the deterministic importer from the repository root:

```powershell
python scripts/import_manual_style.py --source-name "中文风格名" --generation-name "English Generation Style Name" --traits "正向可见特征" --image "C:\absolute\path\representative.png"
```

- Omit `--traits` for name-only input.
- For traits-only input, pass the names you created with `--source-name` and `--generation-name`.
- Use `--dry-run` before importing when checking the selected activation policy would be useful.
- The importer assigns the next number, creates a 512px numbered tile, and continues the active H contact sheet. A single supplied or generated representative image does not create a reference grid; the numbered single image is used if a reference is required. A 1024px 2×2 reference grid is created only when two to four source images are supplied. The importer then updates the source table and capability metadata, rebuilds the gallery, and runs full validation.

Manual styles use a number-only gallery badge. Do not add a fictitious author handle. Report the number, activation path, whether an image was generated or supplied, the active H sheet, and the validation result.
