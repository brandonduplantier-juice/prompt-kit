# SIGNATURE

One accent color, one type family, one data palette. Applied to the same places every time.

The point is recognition, not decoration. A signature works because it is small and it
never changes. Color everywhere is not a signature, it is noise.

## The single most important rule

**Chrome is identity. Data color is not.**

The teal is for headers, links, borders, tags, the KPI number, the rule under a section
heading. It never encodes a data value. The data palette is a separate set, chosen for
perception, and it stays that way even though it does not "match" the teal.

The reason: a dashboard's job is to encode information. The moment you pick series colors
because they are your brand colors, you have made the chart worse to make it prettier.
Roughly 1 in 12 men cannot reliably distinguish red from green. A palette that says good
in green and bad in red is broken for them, and it is broken silently, because they will
not tell you.

So the data palette is Okabe and Ito's colorblind-safe qualitative set, published for
exactly this purpose. Source: Okabe M, Ito K, "Color Universal Design",
https://jfly.uni-koeln.de/color/ . Good is blue `#0072B2`, bad is orange `#D55E00`.
Never green and red.

And even with a safe palette: never rely on hue alone. Pair it with a label, a shape, or
a position.

## The values

| Role | Hex | Use |
|---|---|---|
| accent | `#0B5D5B` | headers, links, borders on hover, tags, section rule |
| accent hover | `#0F7A77` | link hover only |
| accent wash | `#E6F0F0` | tag background, sequential low end |
| ink | `#14181B` | body text |
| muted | `#4A5457` | labels, axis text, secondary text |
| line | `#DDE2E3` | borders, gridlines |
| paper | `#F7F8F8` | page background |
| surface | `#FFFFFF` | cards, chart backgrounds |

Data series, in order: `#0072B2` `#E69F00` `#009E73` `#CC79A7` `#56B4E9` `#D55E00`
`#F0E442` `#000000`

Type: IBM Plex Sans, IBM Plex Mono for anything numeric. Both SIL Open Font License, free.

The recurring mark: a 40px, 2px accent rule under section headings. That, the mono
numbers, and the teal links are the whole signature. Nothing else.

## Measured, not guessed

Contrast ratios computed, not eyeballed. WCAG AA body text needs 4.5, AAA needs 7.

| Pair | Ratio | Verdict |
|---|---|---|
| accent on white | 7.69 | AAA |
| accent on paper | 7.23 | AAA |
| ink on white | 17.85 | AAA |
| muted on white | 7.79 | AAA |

Closest perceptual distance from the accent to any data color: dE 36.9. Above 20 reads as
clearly different, so the chrome will never be mistaken for a data series.

Rejected during design: `#11807C` scored 4.48 on paper, which fails AA by 0.02. It is not
in the palette.

## Why these choices, so you can argue with them

1. **Teal, not blue.** The default blue (`#0d6efd`, `#1f77b4`) is what every untouched
   template ships with. Teal reads adjacent without reading generic. It also sits away
   from red and green, so it never collides with good/bad encoding.
2. **IBM Plex, not Inter.** Inter is the current default of every developer portfolio, so
   it is invisible. Plex has a real mono companion for numbers and code, reads technical
   rather than startup, and is free.
3. **Mono for numbers.** Tabular figures line up in columns instead of jittering. On a
   dashboard full of numbers this is the detail that separates careful from not.

## Where this applies

1. Portfolio site and any Flask app: `tokens.css`
2. Streamlit: `streamlit-config.toml` to `.streamlit/config.toml`
3. Power BI: import `powerbi-theme.json`
4. Tableau: merge `tableau-Preferences.tps` into your Preferences.tps
5. Python figures: `brandon.mplstyle`
6. Looker Studio: no theme file exists. Set it by hand, once, and duplicate that report as
   your template rather than starting fresh each time.

## Where this must NOT apply

These are not stylistic preferences. Each one has a specific cost.

1. **Your resume and cover letters.** Applicant tracking systems parse text. Non-standard
   fonts and colored text are a known parsing risk, and you cannot see the parsed output.
   A resume that a human loves and a parser mangles never reaches the human. Keep them
   plain. You are trading a signature for a job.
2. **Client work for Duplantier Advertising.** The client's brand wins. Putting your teal
   in their report is a small tell that you are running a template, and it is the wrong
   kind of signature.
3. **Nalaquq and QSAR.** Not your project, and it is search and rescue. Legibility under
   bad conditions beats identity, always.
4. **Anything where a convention already exists in the domain.** Reusing a domain's
   established encoding is more useful than being recognizable.

## The honest limits

1. **You cannot have one font everywhere.** Power BI and Tableau render on the viewer's
   machine using the viewer's installed fonts. If they do not have IBM Plex, it falls back
   silently and your report looks different than you built it. This is why the Power BI
   theme specifies Segoe UI, the Windows default, and not Plex. The web gets Plex, shared
   BI reports get Segoe UI. That is the tradeoff and there is no way around it short of
   asking every viewer to install a font, which nobody will do.
2. **The Power BI theme file is syntax-valid but not import-tested.** I validated the JSON.
   I have not loaded it into Power BI Desktop. Power BI silently ignores properties it does
   not recognize rather than erroring, so an ignored property looks identical to a working
   one. Import it, look at it, and tell me what did not take.
3. **The Tableau .tps is well-formed XML but not Tableau-tested.** Same caveat.
4. **The Streamlit config is valid TOML and matches the current docs**, but the docs change
   and my check was made on one date. If a key stops working, check the docs, not me.
5. **This does not match your existing portfolio site.** I have not seen its CSS. If the
   live site already has a color scheme, you now have two identities, which is worse than
   having none. Paste `src/App.jsx` or your stylesheet and I will either retune these
   tokens to what is already there or give you the migration.

## Changing it

Change `tokens.json` first, then propagate to the other files by hand. There is no build
step generating them, so they will drift if you edit only one. If that becomes a problem,
the fix is a small script, not more discipline.
