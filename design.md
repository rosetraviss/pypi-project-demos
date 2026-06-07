# Design Guidelines for PyPI Demo Workers

This document outlines the visual and user experience standards for the PyPI project demo websites hosted in this repository. All demo applications must look premium, modern, responsive, and follow the layout structure described below.

---

## 1. Visual Aesthetics & Design System

Every demo must feel polished, premium, and professional at first glance. Avoid basic browser styles or generic layouts.

### Typography
- Use clean, modern system fonts or curated Google Fonts.
- **Font Stack**: `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji"`
- Use `monospace` fonts exclusively for code blocks, JSON payloads, and technical outputs (e.g., `ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas`).

### Harmonious Color Palette
Define CSS variables (`:root`) to handle color tokens for light mode (and optionally dark mode). Avoid raw colors (such as pure red, primary blue, or lime green).
```css
:root {
  --bg: #fafafa;
  --fg: #111111;
  --accent: #2563eb;          /* Vibrant modern blue */
  --accent-hover: #1d4ed8;
  --card-bg: #ffffff;
  --border: #e5e5e5;
  --muted: #666666;
  --error: #ef4444;           /* Soft red */
  --success: #10b981;         /* Soft green */
}
```

### Layout & Containers
- Restrict max-width of the main page container (e.g., `max-width: 800px`) for optimal readability.
- Use clean padding and margins (`40px 20px` on desktop, scaled down on mobile).
- Utilize cards (`.card`) to separate the interface into distinct conceptual sections:
  1. **Main Sandbox**: The interactive control area.
  2. **API Documentation**: Code snippets, endpoints, and CLI examples.

### Micro-Animations & Interactivity
- Add smooth transitions (`transition: all 0.2s ease`) for interactive components such as buttons, form fields, and navigation links.
- Interactive elements (like buttons) must scale slightly or shift when clicked (`transform: translateY(1px)` / `:active`).
- Inputs should display a subtle focus ring:
  ```css
  input:focus {
    outline: none;
    border-color: var(--accent);
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
  }
  ```

---

## 2. Page & Layout Structure

Every demo application must include the following structural sections:

### A. Header Section
- Title of the demo (corresponds to the PyPI package name).
- Subtitle explaining exactly what the library does in simple terms.
- Link to the package details page on the parent directory.

### B. Interactive Sandbox
- The playground where users can input parameters and see real-time output.
- Show spinner/loading feedback during network requests or complex processing.
- Display errors gracefully in a dedicated warning box (`--error` background/border).

### C. API Documentation
- A dedicated card or section containing sample `curl` calls and JSON responses.
- Ensures the demo is usable as a developer tool, not just a graphical interface.

### D. Footer Requirements (Mandatory)
Each worker's HTML interface must include a footer that anchors the demo into the broader project scope:
1. **Powered By**: A credit sentence: `"Powered by the [PackageName] library on Cloudflare Python Workers."`
2. **Package Link**: A link to the library's package page on `pypi.rosetraviss.uk` (e.g., `https://pypi.rosetraviss.uk/PackageName`).
3. **Home Link**: A link pointing back to the PyPI project hub at `https://pypi.rosetraviss.uk`.

**Standard Footer HTML Template:**
```html
<footer>
  Powered by the <a href="https://pypi.rosetraviss.uk/[package-name]" target="_blank">[package-name]</a> library on Cloudflare Python Workers. 
  Back to <a href="https://pypi.rosetraviss.uk" target="_blank">pypi.rosetraviss.uk</a>
</footer>
```

---

## 3. Brand Assets (Favicon)

- Every demo worker page **MUST** return a clean SVG favicon instead of triggering a 404 error for `/favicon.ico`.
- Define an inline SVG favicon handler in `on_fetch` to serve the icon directly.
- **Example SVG code**:
  ```xml
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
    <circle cx="50" cy="50" r="45" fill="#2563eb" />
    <text x="50" y="65" font-family="Arial, sans-serif" font-size="40" font-weight="bold" fill="white" text-anchor="middle">[Initial]</text>
  </svg>
  ```
