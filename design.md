---
name: Modern Technical Catalog
colors:
  surface: '#f7f9ff'
  surface-dim: '#bddeff'
  surface-bright: '#f7f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#edf4ff'
  surface-container: '#e2efff'
  surface-container-high: '#d8eaff'
  surface-container-highest: '#cde5ff'
  on-surface: '#001d32'
  on-surface-variant: '#41474f'
  inverse-surface: '#0c334e'
  inverse-on-surface: '#e8f2ff'
  outline: '#717880'
  outline-variant: '#c1c7d0'
  surface-tint: '#1d6296'
  primary: '#145d91'
  on-primary: '#ffffff'
  primary-container: '#3776ab'
  on-primary-container: '#f5f8ff'
  inverse-primary: '#98cbff'
  secondary: '#725c00'
  on-secondary: '#ffffff'
  secondary-container: '#fed33a'
  on-secondary-container: '#715b00'
  tertiary: '#316600'
  on-tertiary: '#ffffff'
  tertiary-container: '#3f8100'
  on-tertiary-container: '#ebffd5'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#cfe5ff'
  primary-fixed-dim: '#98cbff'
  on-primary-fixed: '#001d33'
  on-primary-fixed-variant: '#004a77'
  secondary-fixed: '#ffe082'
  secondary-fixed-dim: '#ecc228'
  on-secondary-fixed: '#231b00'
  on-secondary-fixed-variant: '#564500'
  tertiary-fixed: '#a5f866'
  tertiary-fixed-dim: '#8adb4d'
  on-tertiary-fixed: '#0b2000'
  on-tertiary-fixed-variant: '#255100'
  background: '#f7f9ff'
  on-background: '#001d32'
  surface-variant: '#cde5ff'
typography:
  headline-xl:
    fontFamily: Inter
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 44px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  code-md:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 22px
  code-sm:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 18px
  label-caps:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  base: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  container-max: 1200px
  gutter: 24px
---

## Brand & Style

This design system is engineered for the developer ecosystem, specifically targeting a Python package catalog. The brand personality is **precise, authoritative, and efficient**. It prioritizes technical utility over decorative flair, aiming to evoke a sense of reliability and institutional trust.

The design style follows a **Modern Technical** aesthetic. It blends elements of **Minimalism** with a **Systematic** approach:
- **Cleanliness:** Ample whitespace ensures focus on package metadata and documentation.
- **Precision:** Subtle 1px borders and a strict grid provide a sense of architectural integrity.
- **Developer-Centric:** Monospaced typography is elevated from a secondary element to a primary signifier of technical depth.
- **Density:** Information is organized into logical tiers to support quick scanning by experienced users.

## Colors

The palette is rooted in the "Pythonic" heritage, using deep blues to establish authority and trust.

- **Primary (#3776AB):** Used for primary actions, active navigation states, and brand-critical identifiers.
- **Secondary (#FFD43B):** Reserved for highlights, notifications, and "trending" badges. It should be used sparingly to maintain the professional tone.
- **Tertiary/Success (#4E9A06):** A soft mint/green used for version numbers, "verified" badges, and status indicators.
- **Neutral (#1F425E):** A deep slate blue used for text and structural elements like borders and icons to keep the UI softer than pure black.
- **Backgrounds:** A crisp white (#FFFFFF) is the default, with a subtle slate-gray surface (#F8FAFC) used to differentiate card sections and code containers.

## Typography

The typography strategy leverages **Inter** for its exceptional legibility in UI contexts and **JetBrains Mono** for technical data.

- **Inter:** Used for all prose, headings, and interface controls. Headings use tight letter spacing and heavier weights to command attention.
- **JetBrains Mono:** This is the "functional" font. It must be used for package names in search results, version strings, terminal commands (`pip install`), and code blocks.
- **Scale:** On mobile devices, `headline-xl` should scale down to 28px (`headline-lg`) to prevent excessive wrapping.

## Layout & Spacing

The layout uses a **Fixed Grid** system centered on a 12-column structure for desktop. 

- **Desktop (1200px+):** 12 columns, 24px gutters, 32px side margins.
- **Tablet (768px - 1199px):** 8 columns, 16px gutters, 24px side margins.
- **Mobile (<767px):** 4 columns, 16px gutters, 16px side margins.

Information density is maintained by using a tight 4px base unit. Package lists should feel compact, using `spacing.md` for vertical padding between items, while major sections use `spacing.xl` to provide breathing room.

## Elevation & Depth

This system uses **Tonal Layers** combined with **Low-Contrast Outlines** to create hierarchy without visual clutter.

- **Level 0 (Background):** Pure white (#FFFFFF).
- **Level 1 (Cards/Containers):** A surface tint of #F8FAFC with a 1px border of #E2E8F0.
- **Level 2 (Hover/Active):** When a card is hovered, apply a very soft ambient shadow: `0 4px 12px rgba(31, 66, 94, 0.08)`.
- **Level 3 (Modals/Popovers):** Standard shadow `0 12px 24px rgba(31, 66, 94, 0.12)` with a 1px border.

The goal is to keep the interface "flat-adjacent," using depth only to indicate interactivity or focus.

## Shapes

The design system utilizes **Soft** roundedness (0.25rem) to balance the technical "rigidity" with modern UI friendliness.

- **Standard Elements:** Buttons, input fields, and small cards use `rounded` (4px).
- **Large Components:** Hero sections and code containers use `rounded-lg` (8px).
- **Status Badges:** Use `rounded-xl` (12px) or full pill-shape for "Trending" and "Stable" tags to differentiate them from functional buttons.

## Components

### Search Bar
Large, centered input field. Uses `body-lg` text. Features a prominent `primary` border on focus and a "slash" shortcut hint (`/`) in monospaced font.

### Package Cards
- **Title:** `headline-md` using `neutral` blue.
- **Metadata:** Monospaced `code-sm` for version and license.
- **Description:** `body-sm` limited to two lines.
- **Badge:** "Trending" badges use the `secondary` yellow background with dark neutral text.

### Code Snippets
Containers use the `surface` background color with a 1px border. Always use `code-md` for the content. Syntax highlighting should follow a "Sublime" or "VS Code" inspired theme that complements the primary blue palette.

### Resource Link Cards
Small, grid-based cards for "GitHub", "PyPI", and "Docs". Use small icons with `neutral` stroke and `label-caps` for the text.

### Buttons
- **Primary:** Solid `primary` blue with white text.
- **Secondary:** Outline button with `primary` blue border and text.
- **Ghost:** No border, `neutral` text, used for less important actions like "Copy License".