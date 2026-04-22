# GhostOffice Design System
# Drop this file in the root of the OfficeGhost repo.
# OpenCode reads project files — every UI task will inherit this identity.

## Identity
GhostOffice is a **privacy-first local AI productivity tool** for professionals.
Aesthetic direction: **dark premium** — the feel of Linear, Vercel, or Raycast.
Not a startup toy. Not a hackathon project. A serious tool that respects the user.

---

## Color Tokens

Use these EXACT values as CSS variables. Never deviate.

```css
:root {
  /* Backgrounds — layered depth */
  --bg-base:        #0A0A0B;    /* page background — near black */
  --bg-surface:     #111113;    /* cards, panels */
  --bg-elevated:    #1A1A1E;    /* modals, dropdowns, hover surfaces */
  --bg-subtle:      #222228;    /* input backgrounds, code blocks */

  /* Borders */
  --border-default: #2A2A32;    /* default border */
  --border-strong:  #3A3A45;    /* focused, active borders */
  --border-glow:    #F59E0B40;  /* amber glow border on focus/hover */

  /* Amber Accent — the soul of GhostOffice */
  --accent:         #F59E0B;    /* primary amber */
  --accent-hover:   #FBBF24;    /* lighter on hover */
  --accent-dim:     #F59E0B20;  /* subtle amber tint backgrounds */
  --accent-glow:    0 0 20px #F59E0B35; /* box-shadow glow */

  /* Text hierarchy */
  --text-primary:   #F1F0EE;    /* headlines, important content */
  --text-secondary: #A09FA6;    /* body copy, descriptions */
  --text-muted:     #5C5B63;    /* timestamps, captions, placeholders */
  --text-accent:    #F59E0B;    /* links, highlights, active labels */

  /* Semantic */
  --success: #10B981;
  --warning: #F59E0B;
  --error:   #EF4444;
  --info:    #6366F1;
}
```

---

## Typography

**Display / Headings:** `"Syne"` — geometric, architectural, premium feel
**Body:** `"DM Sans"` — clean, readable, professional
**Code / Mono:** `"JetBrains Mono"` — sharp, developer-native

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=DM+Sans:wght@300;400;500&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
```

Scale:
```
11px  → captions, badges
13px  → secondary labels, nav items
15px  → body text
18px  → subheadings
24px  → section titles
32px  → page titles
48px  → hero/display
```

Rules:
- Headings: Syne, font-weight 700, letter-spacing -0.02em
- Body: DM Sans, font-weight 400
- Numbers/data/code: JetBrains Mono always
- NEVER use Inter, Roboto, Arial, Space Grotesk, or system-ui as primary fonts

---

## Spacing System

Base unit: 4px. Always use multiples.

```
4px  → tight inline gaps, icon spacing
8px  → between related elements
12px → component internal padding (small)
16px → standard padding
24px → card padding, section gaps
32px → between components
48px → section padding
64px → page section breaks
```

---

## Component Specs

### Cards
```css
background: var(--bg-surface);
border: 1px solid var(--border-default);
border-radius: 8px;  /* NOT 12px or 16px — keep it sharp */
padding: 24px;
transition: border-color 200ms ease, box-shadow 200ms ease;

/* Hover — amber glow, not just border change */
&:hover {
  border-color: var(--border-strong);
  box-shadow: var(--accent-glow);
}
```

### Buttons
```css
/* Primary */
background: var(--accent);
color: #0A0A0B;
font-family: 'DM Sans';
font-weight: 500;
font-size: 13px;
padding: 8px 16px;
border-radius: 6px;
letter-spacing: 0.01em;
&:hover {
  background: var(--accent-hover);
  box-shadow: 0 0 16px #F59E0B50;
}

/* Ghost / Secondary */
background: transparent;
border: 1px solid var(--border-default);
color: var(--text-secondary);
&:hover {
  border-color: var(--border-strong);
  color: var(--text-primary);
  background: var(--bg-elevated);
}

/* Danger */
background: transparent;
border: 1px solid #EF444440;
color: #EF4444;
&:hover { background: #EF444415; border-color: #EF4444; }
```

### Inputs
```css
background: var(--bg-subtle);
border: 1px solid var(--border-default);
border-radius: 6px;
padding: 10px 14px;
color: var(--text-primary);
font-family: 'DM Sans';
font-size: 14px;
&:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-dim);
}
```

### Badges / Status Pills
```css
/* Active / Running */
background: var(--accent-dim);
color: var(--accent);
border: 1px solid #F59E0B30;
border-radius: 4px;
padding: 2px 8px;
font-family: 'JetBrains Mono';
font-size: 11px;
font-weight: 500;
letter-spacing: 0.05em;
text-transform: uppercase;
```

### Sidebar / Nav
```css
/* Container */
background: var(--bg-surface);
border-right: 1px solid var(--border-default);
width: 240px;

/* Nav item default */
padding: 8px 12px;
border-radius: 6px;
color: var(--text-secondary);
font-size: 13px;

/* Active nav item */
background: var(--accent-dim);
color: var(--accent);
border-left: 2px solid var(--accent);
font-weight: 500;
```

---

## Background Texture

Always apply subtle noise grain to body for depth:

```css
body::before {
  content: '';
  position: fixed;
  inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E");
  pointer-events: none;
  z-index: 0;
}
```

---

## Layout Rules

- Max content width: `1160px`, centered
- Sidebar + main: `240px | 1fr`
- Grid gaps: 16px tight / 24px standard / 32px loose
- **Layouts are left-aligned and asymmetric** — not centered hero columns
- Data/metrics: JetBrains Mono, numbers right-aligned, labels left-aligned
- Section dividers: `1px solid var(--border-default)` only — no decorative HR

---

## Motion

```css
/* Standard easing — professional, no bounce */
transition: all 200ms cubic-bezier(0.4, 0, 0.2, 1);

/* Hover lift on cards */
transform: translateY(-1px);

/* Page load stagger */
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}
.card                { animation: fadeUp 300ms ease forwards; }
.card:nth-child(2)   { animation-delay: 60ms; }
.card:nth-child(3)   { animation-delay: 120ms; }
.card:nth-child(4)   { animation-delay: 180ms; }
```

Rules:
- No bounce, spring, or playful easing — professional tool, serious feel
- Duration range: 150ms–300ms only
- Only animate `transform` and `opacity` — never layout properties

---

## BANNED — Never Use These in GhostOffice

```
Fonts:    Inter, Roboto, Arial, Space Grotesk, Nunito, Poppins, system-ui
Colors:   indigo-600 as primary, purple gradients, white/light backgrounds,
          gray-900 or zinc-900 (too generic — use #0A0A0B)
Radius:   rounded-xl (16px+) on cards, rounded-full on non-pill elements
Shadows:  large diffuse shadows: box-shadow 0 25px 50px rgba(0,0,0,0.5)
Layouts:  centered hero with gradient blob behind title
          card grid of identical rounded-xl shadow-md cards
          sidebar with emoji-only icons as nav labels
          full-width indigo/violet gradient banner
          "Get Started" button in indigo-600
```

---

## GhostOffice UI Checklist

Before finishing any UI component, verify every item:

- [ ] Background is `#0A0A0B` or `#111113` — not gray-900 or zinc-900
- [ ] Accent color is amber `#F59E0B` — not indigo, violet, or blue
- [ ] Headings use Syne font — not Inter or system-ui
- [ ] Body uses DM Sans — not Inter
- [ ] Numbers/data/code use JetBrains Mono
- [ ] Card border-radius is 8px max — not 12px or 16px
- [ ] Hover states show amber glow — not just border color change
- [ ] Layout is left-aligned / asymmetric — not centered column
- [ ] Noise grain texture applied to body
- [ ] No light mode styles unless explicitly requested
