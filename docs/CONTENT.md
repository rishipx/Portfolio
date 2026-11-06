# Content guide

Everything personal lives in `content/`. Run `python scripts/build.py --serve` and refresh after each change.

## Your details: `content/site.json`

| Field | Notes |
|---|---|
| `name`, `heading`, `role`, `tagline`, `description` | Hero text and page metadata |
| `email`, `github`, `location` | Hero buttons and tooltip |
| `projects_title` | Optional heading above the project grid |
| `stats` | List of `{ "value", "label" }` |
| `work`, `education` | Lists of `{ "initials", "org", "dates", "role", "bullets" }` |
| `skills` | Groups of names, for example `[["Python", "Linux"], ["Docker"]]`. Icons come from `src/data/tech.json` |

Replace the files in `content/profile/`: `resume.pdf`, `og-image.png` (1200x630 social preview) and `favicon.svg`.

## Add a project

Create `content/projects/weather-cli/` with these files:

```json
{
  "title": "Weather CLI",
  "kicker": "Command Line",
  "summary": "Prints a clean forecast in your terminal.",
  "stack": ["Python", "Docker"],
  "website": "https://example.com/weather-cli",
  "source": "https://github.com/your-username/weather-cli",
  "order": 15
}
```

Add `cover.webp` (or `.png`, `.jpg`, `.svg`) and an optional `README.md` for the dialog.

| Field | Required | Notes |
|---|---|---|
| `title`, `summary`, `kicker` | yes | `kicker` is the small label above the dialog title |
| `stack` | no | Badges in the dialog. Names found in `src/data/tech.json` also show as icons on the card |
| `icons` | no | Override which technologies get card icons, and their order |
| `website`, `source` | no | Leave one out to hide its icon on the card and in the dialog |
| `order` | no | Lower numbers first. Use gaps (10, 20, 30) |
| `draft` | no | `true` keeps it out of the build |

## Add a post

Case studies, guides and write-ups live in `content/posts/<slug>/post.json`. They share the project grid and use the
same fields, plus:

| Field | Notes |
|---|---|
| `kind` | Required. `case-study`, `guide` or `write-up`: becomes the pill on the card |
| `date` | Required. `YYYY-MM-DD` |
| `tag` | Optional custom pill text instead of the `kind` label |

`kicker` is optional for posts.

## Ordering

Items with an `order` come first, lowest number first, projects and posts mixed. The rest follow: projects by title,
then posts newest first.

## Writing `README.md`

Supported Markdown: headings, paragraphs, lists, quotes, code fences, links, `**bold**`, `*italic*`, `` `code` `` and
images. Image paths are relative to the folder, for example `images/screen.png`. An image on its own line becomes a
figure and its title becomes the caption:

```markdown
![Dashboard](cover.webp "Shown under the image")
```

## Technology icons

`src/data/tech.json` maps technology names to icons. Add an entry (with optional `aliases`) to give a new technology a
card icon or a place in the skills list. Names that are not in the file still appear as badges in the dialog.

## Build errors

The build stops with a clear message when a required field, cover image, date, kind or URL is wrong, and when two
folders use the same slug.
