<div align="center">

<img src="99-attachments/readme/hero.jpg" width="100%" alt="Quatre axes : mouvements, dessin, cinéma">

# Bibliothèque d'esthétique artistique

**Le style visuel, décomposé en couches de prompt réellement appelables**

Mouvements · Dessin · Réalisateurs · Mouvements de caméra — quatre axes, une structure

[![DeepSeek Harness](https://img.shields.io/badge/DeepSeek%20Harness-dsh--plugin-4D6BFE?style=flat-square)](https://github.com/deepseek-ai/deepseek-harness)
[![Agent Skill](https://img.shields.io/badge/Agent-Skill-7C3AED?style=flat-square)](.repo/skill)
[![License](https://img.shields.io/github/license/YanKaFei/art-aesthetic-vault?style=flat-square)](LICENSE)

`421 mouvements` · `274 styles dessinés` · `100 films` · `157 recettes de plan` · `686 notes` · `746 images`

[中文](README.md) ｜ [English](README.en.md) ｜ [日本語](README.ja.md) ｜ **Français**

</div>

---

## Qu'est-ce que c'est

La plupart des gens collectionnent les références de style en enregistrant des images.
On finit avec quelques centaines de fichiers et aucune idée de quoi regarder ni de
comment le décrire. Les images ne servent à rien toutes seules.

Cette bibliothèque fait autrement : **elle décompose chaque langage visuel en sept
couches remplaçables indépendamment.**

<img src="99-attachments/readme/layers.png" width="100%" alt="Sept couches : style / lumière / couleur / composition / matière / ambiance / caméra">

Une fois découpé en couches, vous pouvez poser la lumière de l'image A sur le sujet
de l'image B. **C'est là tout l'intérêt d'une bibliothèque de références.**

```bash
python3 artvault.py compose \
  "un chasseur de primes dans une rue néon sous la pluie, lumière baroque, cadrage cyberpunk" \
  --subject "a female bounty hunter in a wet neon alley"
```

L'outil lit l'intention derrière chaque groupe de mots (« baroque » suivi de
« lumière » prend la couche lumière du baroque), puis produit des prompts positifs
en couches, des prompts négatifs, une palette, une couche vidéo et un
**journal de résolution des conflits**.

> **Même sujet, chaque couche interchangeable.** C'est la différence avec un simple
> tas de mots-clés de style.

---

## Quatre axes

Les quatre axes partagent la même structure de fiche et le même vocabulaire de sept
couches : on peut donc les mélanger — la lumière d'un film + la palette d'un
mouvement + la matière d'un dessin.

| | Axe · ampleur | À quoi cela répond |
|---|---|---|
| <img src="99-attachments/readme/axis-1-movements.jpg" width="300" alt="Mouvements artistiques"> | **Mouvements · 421**<br>（7 catégories） | De Byzance à Y2K, de l'ukiyo-e au cyberpunk. Une fiche par mouvement : analyse visuelle en 6 axes + 7 couches de prompt + palette de 6 couleurs + négatifs ciblés + couche vidéo<br>`python3 artvault.py layers 巴洛克` |
| <img src="99-attachments/readme/axis-2-handraw.jpg" width="300" alt="Styles dessinés"> | **Styles dessinés · 274**<br>（groupes A à H） | Albums, caricature de presse, illustration contemporaine, guofeng… issus de [handraw-style](https://github.com/yang0/handraw-style) (**MIT**), intégrés en entier. Les fiches sont nommées en chinois, le numéro d'origine restant un alias<br>`python3 artvault.py layers 极端比例弯曲绘本` |
| <img src="99-attachments/readme/axis-3-films.jpg" width="300" alt="Réalisateurs et films"> | **Réalisateurs et films · 100**<br>（44 réalisateurs） | Pas seulement « à quoi ça ressemble » mais « qui l'a filmé et comment ». Organisé réalisateur puis film : images représentatives + analyse en 6 axes + 7 couches + palette + couche vidéo, plus **6142 liens externes vers des photogrammes** (indexés, jamais réhébergés)<br>`python3 artvault.py film show dune` |
| <img src="99-attachments/readme/axis-4-shots.jpg" width="300" alt="Recettes de plan"> | **Recettes de plan · 157**<br>（10 catégories） | Les trois premiers axes répondent à « à quoi ça ressemble » ; celui-ci répond à « **comment produire ce mouvement** ». Images, easing et amplitude en tableaux de paramètres, avec les pièges connus. Issu de [video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft) (**Apache-2.0** — cette bibliothèque ne fait que classer et mettre en forme)<br>`python3 artvault.py shots show crash-zoom-punch` |

> ⚠ **Les fiches de plan n'ont volontairement ni couleur ni lumière.** Elles parlent
> de nombres d'images et d'easing (`zoom 6f ease-in, 1 à 2.6`) ; les forcer dans les
> sept couches reviendrait à inventer du contenu. Elles portent donc leurs propres
> quatre champs et **restent hors de la résolution de couches de `compose`** —
> un test garde cette frontière.

---

## En un coup d'œil

<img src="99-attachments/readme/gallery.jpg" width="100%" alt="Exemples de mouvements, de dessins et de films présents">

| | |
|---|---|
| **Fiches de mouvement** | **421 fiches**, en 7 catégories. Chacune : analyse visuelle en 6 axes, 7 couches de prompt, palette de 6 couleurs, couche vidéo et pièges connus |
| **Images** | **746** (167 Mo) = **452** images de musée du domaine public + **294** planches numérotées handraw-style (MIT) ; couvrant 359 mouvements |
| **Noms des fiches dessinées** | **274 / 274** nommées (249 tirées mot pour mot des `traits` ; 25 rétro-traduites du nom de génération anglais quand `traits` est vide) |
| **Guides et méthode** | 15 notes (vue d'ensemble, atlas de mots-clés, la méthode des 7 couches, structure vidéo, index des palettes…) |
| **Atlas de mots-clés** | Les **4 groupes de concepts les plus confondus**, **46 synonymes** au total — cherchez n'importe lequel et vous arrivez sur la même fiche |
| **Fiches de film** | **100 fiches** (44 réalisateurs), organisées réalisateur puis film : index de photogrammes + analyse en 6 axes + 7 couches + palette + couche vidéo, plus **6142 liens externes** (indexés, jamais réhébergés) |
| **Fiches de plan** | **157 fiches** (10 catégories) : mouvements de caméra et effets avec tableaux de paramètres (images/easing/amplitude) et pièges connus. Depuis [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft), **Apache-2.0 — cette bibliothèque ne fait que classer et mettre en forme** |
| **Modèles de note** | 3 |
| **Scripts** | 65 — récupération, génération, recherche, composition, serveur MCP |

> **62 mouvements sont des « fiches prompt seul ».** Expressionnisme abstrait,
> pop art, minimalisme, art conceptuel, cyberpunk, vaporwave : il n'existe
> pratiquement pas d'images librement rediffusables pour ceux-là. Leur langage visuel
> et leurs sept couches sont analysés normalement ; ils n'ont simplement pas d'image.
> C'est un choix délibéré, pas une lacune.

---

## Comment l'utiliser

### 1. Le lire comme un coffre Obsidian

Ouvrez ce dossier dans Obsidian. Un bon ordre de parcours :

1. `00-guides/提示词拆解方法.md` — **commencez ici** pour comprendre les sept couches
2. `00-guides/流派总览.md` — l'index général de tous les mouvements
3. `10-movements/` — choisissez un mouvement et lisez son analyse complète
4. `00-guides/关键词图谱.md` — pour chercher plus tard un terme inconnu

### 2. Laisser une IA l'appeler

Ce n'est pas seulement du Markdown pour humains ; il y a une **interface pour la machine** :

```bash
cd .repo

python3 artvault.py categories              # les 7 catégories
python3 artvault.py search "néon pluie"     # recherche floue, chinois ou anglais
python3 artvault.py search "lumière oppressante mais somptueuse" --semantic
python3 artvault.py layers baroque          # seulement les sept couches (le moins de tokens)
python3 artvault.py show ukiyo-e            # la fiche complète
python3 artvault.py palette cyberpunk       # la palette de six couleurs
python3 artvault.py related cubism          # mouvements voisins

python3 artvault.py film list               # 100 films
python3 artvault.py shots search "crash zoom punch"

python3 artvault.py --json layers baroque   # lisible par machine
```

**La composition est la capacité centrale** :

```bash
# langage naturel, découpage automatique en couches
python3 artvault.py compose "un chasseur de primes sous le néon, lumière baroque" \
  --subject "a bounty hunter"

# explicite, en mélangeant les époques
python3 artvault.py compose --style ukiyo-e --lighting baroque \
  --color vaporwave --composition precisionism --subject "a lone samurai"

# entre axes : la lumière d'un film + la palette d'un mouvement
python3 artvault.py compose --lighting villeneuve-dune --color baroque \
  --subject "a lone figure on a dune"
```

L'outil **résout automatiquement les conflits de couches**. En mélangeant des
mouvements, leurs prompts négatifs se contredisent — l'ukiyo-e interdit
`cast shadows`, la lumière baroque exige `deep crushed shadows` ; le précisionnisme
interdit `people` alors que votre sujet *est* une personne.
**Le modèle ne renvoie pas d'erreur** ; vous obtenez seulement des « images
bizarrement mauvaises », ce qui est extrêmement difficile à diagnostiquer. Les
négatifs en conflit sont donc **retirés du prompt négatif** et listés un par un sous
« conflits résolus automatiquement », en indiquant ce qui a été retiré et à quoi il
a cédé. La règle en une ligne : **les positifs sont l'intention, les négatifs sont
des garde-fous, et les garde-fous cèdent devant l'intention.** Ajoutez
`--keep-conflicts` pour voir l'union brute et juger vous-même.

### 3. L'installer comme skill d'IA (recommandé)

Le dépôt fournit deux skills. Une fois installés, **tout assistant IA compatible**
consultera cette bibliothèque pour les tâches visuelles ou esthétiques au lieu
d'inventer de la terminologie de mémoire.

```bash
cd .repo/skill && ./install.sh
```

| skill | Rôle | Se déclenche quand |
|---|---|---|
| `art-aesthetic-vault` | **Utiliser** la bibliothèque : chercher un mouvement, extraire les sept couches, composer | Vous demandez « quel style pour ce personnage ? » |
| `build-art-aesthetic-vault` | **Construire** une bibliothèque de zéro | Vous dites « je veux la même chose » |

> [!note] Pourquoi aucun skill n'embarque les données
> Les deux sont des **liens symboliques** vers ce dépôt — il n'y a qu'une seule copie
> des données. Si `mv_*.py` (les définitions de mouvements) étaient empaquetés dans
> le skill, il y aurait deux copies et elles divergeraient forcément. Testé : la
> version empaquetée avait 4 fichiers désynchronisés, et les bibliothèques
> construites avec elle avaient de mauvaises catégories.

Il crée les liens dans tous les répertoires de skills trouvés :

| Répertoire | Lu par |
|---|---|
| `~/.agents/skills/` | DSH / Codex / convention générale |
| `~/.claude/skills/` | Claude Code |
| `~/.codex/skills/` | Codex |

**Pourquoi des liens symboliques** : le skill résout sa propre position réelle avec
`pwd -P` et en déduit la racine du dépôt — **où qu'il soit, et même déplacé, il est
retrouvé automatiquement**, sans aucune configuration.

```bash
.repo/skill/install.sh --copy        # installer par copie (à refaire si le dépôt bouge)
.repo/skill/install.sh --uninstall
bash .repo/skill/locate.sh           # localiser le dépôt manuellement (diagnostic)
```

Les skills prennent effet dans une **nouvelle session d'IA**.

### 4. Le brancher en MCP (Claude Desktop / Cursor)

```json
{
  "mcpServers": {
    "artvault": {
      "command": "python3",
      "args": ["<chemin absolu de ce dépôt>/.repo/mcp_server.py"]
    }
  }
}
```

16 outils sont exposés : `search_movements` `get_movement` `get_layers`
`compose_prompt` `get_palette` `find_related` `list_categories` `analyze_image`
`match_movement` `get_video_prompt`, plus `search_films` `get_film`
`get_film_layers` `get_film_stills` pour la filmothèque et `search_shots` `get_shot`
pour les plans. Les derniers demandent Pillow / un modèle CLIP ; en leur absence ils
expliquent pourquoi, sans affecter les sept premiers.

---

## Ce qui le distingue

### 1. Pas un pack d'images — une structure composable

Un pack d'images vous donne « l'effet que ça fait » ; ceci vous donne « comment
produire cet effet ». Chaque couche se retire seule : gardez la couche style,
changez le sujet, vous avez un modèle de transfert de style.

### 2. La lumière est une couche à part entière

La plupart des gens écrivent leurs prompts en un bloc et ajustent par essais-erreurs.
Cette bibliothèque l'affirme : **la lumière pèse plus sur le rendu final que les mots
de style.** La couche lumière de chaque mouvement est un bloc séparé, déplaçable sur
un autre sujet.

### 3. Chaque axe a des négatifs ciblés

Visant le mode d'échec **de ce mouvement précis**, pas une liste négative générique :

- Impressionnisme → `black shadows, smooth blending, photorealistic`
- Renaissance → `visible brushstrokes, impasto` (l'IA ajoute de l'empâtement aux huiles)
- Ukiyo-e → `3d shading, cast shadows, gradient` (l'IA ajoute du volume)

**Notez que les négatifs de mouvements différents se contredisent souvent** — c'est
exactement pourquoi les mélanges se battent, et exactement ce que cette bibliothèque
gère pour vous.

### 4. Une IA peut l'utiliser, pas seulement le regarder

Les grands modèles se souviennent vaguement des mouvements artistiques et confondent
régulièrement Art nouveau et Art déco, ou Barbizon et impressionnisme. Cette
bibliothèque fixe la terminologie concrète : une IA qui l'appelle n'inventera rien.

### 5. La terminologie est fixée, pas inventée

L'atlas de mots-clés retient les **4 groupes de concepts les plus
confondus** — avant-garde, contemporain, postmoderne, surréaliste. Chacun reçoit une
définition, plusieurs limites « ce que ce n'est pas », et **46 synonymes** ;
chercher l'un d'eux mène à la même fiche.

### 6. Une image que vous avez déjà peut devenir un prompt vidéo

Les prompts vidéo des fiches sont **génériques** — la ligne du sujet est un
emplacement réservé. Mais ce que vous voulez vraiment, c'est « j'ai cette image,
fais-la bouger » :

```bash
python3 i2v_prompt.py votre-image.jpg --slug baroque
```

Taille de plan, position dans le cadre, direction du mouvement interne, faut-il
animer la lumière, la caméra avance-t-elle ou panoramique-t-elle : tout est dérivé de
**mesures objectives de cette image** (taille de plan par détection de visage / centre
de saillance / direction des lignes / densité de détail / structure clair-obscur),
avec une fiche « base de dérivation » à vérifier. La sortie laisse toujours
« qui, faisant quoi — ajoutez une ligne vous-même » : seul celui qui regarde l'image
le sait, et le script ne l'inventera pas.

### 7. Les chiffres sont calculés, pas écrits en dur

Chaque chiffre « combien y a-t-il dans cette bibliothèque » est calculé par
`publish_stats()` sur la **vue publiée** (ce que git suit, pas ce qui traîne sur la
machine de l'auteur), puis vérifié ligne par ligne par `verify_vault.py`. La seule
chose qu'un chiffre écrit en dur finit toujours par faire, c'est devenir faux —
cette bibliothèque en a fait l'expérience, donc le verrou est là.

---

## Trois principes

1. **Plutôt moins que faux.**
   La sélection refuse délibérément le « élargissons un peu » — si un mouvement n'a
   qu'une image, il en a une. Le vrai danger d'une bibliothèque de références n'est
   pas le manque d'images mais les mauvaises : une mauvaise référence contamine votre
   intuition et vous ne le découvrez jamais.

2. **La lumière compte plus que les mots de style.**
   Si vous ne pouvez régler qu'une couche, réglez la lumière.

3. **N'inventez pas la terminologie de mémoire.**
   La mémoire des grands modèles est floue et confond les écoles voisines.
   Fiez-vous à la terminologie concrète de la bibliothèque.

---

<details>
<summary><b>Déplier l'arbre complet (421 mouvements / 7 catégories)</b></summary>

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

## Crédits et sources

Cette bibliothèque existe parce que des personnes **ont choisi d'ouvrir leur
travail**. Aucun des éléments ci-dessous n'est un simple « nous l'avons consulté » :
chacun a été **repris en entier et redécoupé dans la même structure de fiche** :

| Source | Apport | Licence |
|---|---|---|
| [yang0/handraw-style](https://github.com/yang0/handraw-style) | **274 styles dessinés** et leurs planches numérotées, formant la 7e catégorie | **MIT** |
| [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft) | **157 fiches de recette de plan** (10 catégories) ; cette bibliothèque ne fait que classer et mettre en forme | **Apache-2.0** |
| [film-grab.com](https://film-grab.com/) | L'index de photogrammes de films ; les images représentatives intégrées aux fiches restent la **propriété de leurs ayants droit** | Le site indique : *images are not permitted for commercial use*. Référence d'étude personnelle uniquement |
| [Glossaire Tate](https://www.tate.org.uk/art/art-terms) | Les pages de définition citées dans la section « sources » de chaque fiche — les sept couches remontent à des définitions faisant autorité | Le texte des termes est **copyright Tate** ; cette bibliothèque ne fait que **citer la source** |
| [Cleveland Museum of Art](https://openaccess-api.clevelandart.org) · [Art Institute of Chicago](https://api.artic.edu/docs/) · [Metropolitan Museum](https://collectionapi.metmuseum.org) · [Wikimedia Commons](https://commons.wikimedia.org) | **452 images de musée du domaine public** | **CC0 / domaine public** |

**Trois limites à énoncer clairement** :

1. **Les fiches de plan ne sont pas originales.** Le droit d'auteur sur ces
   157 descriptions de techniques appartient au projet amont (Apache-2.0).
   Cette bibliothèque ne fait que les classer et les mettre en forme, et chaque fiche
   porte le chemin et le commit amont. L'amont précise que les techniques de mouvement
   ont été étudiées à partir d'œuvres publiques, que **toute implémentation a été
   réécrite de zéro** sans aucune image d'origine, et que « publié » **n'est pas**
   synonyme de « sous licence ». N'utilisez pas ces fiches pour reproduire la
   présentation audiovisuelle globale et reconnaissable d'une œuvre précise.
2. **Les photogrammes restent la propriété de leurs ayants droit.** Les images
   intégrées aux fiches sont destinées à la **référence d'étude personnelle** ;
   film-grab précise qu'elles ne peuvent pas être utilisées commercialement. Obtenez
   une autorisation avant toute rediffusion ou usage commercial.
3. **Les « noms d'artistes / styles référencés » sont des étiquettes d'index** — ni
   des descriptions des personnes, ni une consigne d'imitation. Les planches
   numérotées ne servent qu'au style : n'en reprenez ni les sujets, ni les
   compositions, ni les textes.

Les parties propres à cette bibliothèque (décomposition en sept couches, structure
des fiches, CLI / MCP, logique de recherche et de composition) sont publiées sous MIT.

---

## Licence

- **Code et texte des fiches** : [MIT](LICENSE)
- **Images du domaine public** : CC0 / domaine public ; source et licence indiquées dans la section « sources » de chaque fiche
- **Planches numérotées handraw-style** : MIT (amont)
- **Fiches de recette de plan** : Apache-2.0 (amont) ; cette bibliothèque ne fait que classer et mettre en forme
- **Photogrammes de films** : propriété de leurs ayants droit ; référence d'étude personnelle uniquement

---

<div align="center">

Si cela vous est utile, une étoile ⭐ fait plaisir — les PR ajoutant des mouvements sont bienvenues

</div>
