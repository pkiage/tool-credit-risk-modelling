# ADR-015: Dark Mode and Accessibility Standards

| Field | Value |
|-------|-------|
| Status | Accepted |
| Author | Paul / Claude |
| Date | 2026-02-08 |
| PR | [#46](https://github.com/pkiage/tool-credit-risk-modelling/pull/46), [#48](https://github.com/pkiage/tool-credit-risk-modelling/pull/48) |

## Context

The Next.js web application needed dark mode support for developer ergonomics and accessibility. Users working in low-light environments or with visual preferences for dark backgrounds should be accommodated. The implementation also needed to meet color contrast standards for accessibility compliance.

Key requirements:

- Support light, dark, and system-preference themes
- Persist user preference across sessions
- Maintain readable contrast ratios across all themes
- Work with existing Tailwind CSS setup and Recharts visualizations

## Decision

Implement dark mode using **CSS custom properties (variables) with Tailwind CSS class-based toggling** and a custom `ThemeProvider` React context. Target **WCAG AAA color contrast** (7:1 ratio for normal text) across both themes.

### Implementation

1. **ThemeProvider** (`lib/theme-provider.tsx`): Custom React context supporting three modes — `light`, `dark`, `system` — with `localStorage` persistence and `prefers-color-scheme` media query listener
2. **CSS variables** (`globals.css`): Semantic color tokens (e.g., `--foreground`, `--surface`, `--border`) defined for both light and dark themes
3. **ThemeToggle** (`components/ui/theme-toggle.tsx`): Three-state toggle button (light → dark → system) with SVG icons and accessible `aria-label`
4. **Tailwind dark mode**: Configured as `class` strategy, toggled by the ThemeProvider adding/removing `dark` on `<html>`

### Accessibility

- WCAG AAA contrast ratios (7:1) for all text against backgrounds in both themes
- Distinct focus ring styles (`focus:ring-2 focus:ring-focus-ring`)
- `aria-label` on theme toggle with current state
- `aria-hidden="true"` on decorative SVG icons

## Consequences

### Positive

- Users can work in their preferred color scheme
- System preference detection provides good defaults
- CSS variables make it straightforward to add new themed components
- WCAG AAA compliance exceeds most accessibility requirements

### Negative

- Custom ThemeProvider adds client-side JavaScript; brief flash of light theme possible on first load before hydration
- Chart colors (Recharts) must be coordinated with theme variables — each new chart must consider both themes
- Two color palettes to maintain going forward

### Neutral

- Gradio and Marimo layers are unaffected — they use their own theming systems
- The approach does not use `next-themes` (a popular library) to avoid an extra dependency for a straightforward use case

## Alternatives Considered

### Alternative 1: next-themes library

Drop-in dark mode for Next.js with SSR flash prevention via script injection.

**Why not chosen:** Adds a dependency for functionality achievable with ~70 lines of custom code. The custom ThemeProvider is simpler to understand and modify.

### Alternative 2: Tailwind `media` strategy

Use `@media (prefers-color-scheme: dark)` instead of class-based toggling.

**Why not chosen:** No manual override — users cannot choose a theme different from their OS preference. The three-state toggle (light/dark/system) requires class-based control.

### Alternative 3: WCAG AA instead of AAA

Target 4.5:1 contrast ratio (AA) instead of 7:1 (AAA).

**Why not chosen:** The stricter AAA standard was achievable with minimal design trade-offs and provides better readability for all users.
