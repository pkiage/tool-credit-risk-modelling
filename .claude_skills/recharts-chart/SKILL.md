---
name: recharts-chart
description: Create new Recharts visualization components following the project's proven chart patterns (responsive, typed, dark-mode compatible).
---

# Recharts Chart Skill

Generate new chart components that match the conventions established across the 3 existing Recharts chart types (`ROCCurve`, `CalibrationPlot`, `MetricsBar`) in `apps/web/components/charts/`.

## When to Use

- Adding a new visualization to the Next.js dashboard
- Creating a chart component for a new model metric
- Building single-series or multi-series comparisons

## When NOT to Use

- Non-chart UI components (use shadcn/ui patterns instead)
- Custom HTML visualizations like the confusion matrix grid
- Charts that don't use Recharts (e.g., D3-only)

## Chart Types Available

| Recharts Component | Use When | Example in Codebase |
|--------------------|----------|---------------------|
| `LineChart` | Continuous x-y data, curves | ROC curve, calibration plot |
| `BarChart` | Categorical comparisons | Metrics comparison across models |
| `AreaChart` | Line with filled region | Probability distributions |
| `ScatterChart` | Discrete x-y points | Feature importance scatter |

## Creation Steps

1. **Define the TypeScript interface** in `apps/web/lib/types.ts`
   - Match the Pydantic schema structure from `shared/schemas/`
   - Use arrays for series data (e.g., `fpr: number[]`, `tpr: number[]`)

2. **Create the component** in `apps/web/components/charts/<name>.tsx`
   - Follow the template in `references/chart-template.tsx`
   - Start with `"use client"` directive
   - Single default or named export

3. **Add data transformation** (if needed)
   - Transform parallel arrays into Recharts point objects inside the component
   - Keep transformation minimal; prefer shaping data at the page level

4. **Integrate into a page**
   - Wrap in a `<Card>` component with a descriptive title
   - Pass typed props from API response data

## Conventions

### Component Structure

Every chart component follows this order:

```tsx
"use client";

// 1. Recharts imports (destructured)
import { CartesianGrid, Line, LineChart, ... } from "recharts";

// 2. Type imports
import type { DataType } from "@/lib/types";

// 3. Props interface
interface ChartNameProps { ... }

// 4. Constants (colors, labels)
const COLORS = ["#2563eb", "#dc2626", "#16a34a", "#9333ea", "#ea580c"];

// 5. Component function
export function ChartName({ data }: ChartNameProps) { ... }
```

### Dimensions

- **Height**: Always `350` via `ResponsiveContainer`
- **Width**: Always `"100%"` via `ResponsiveContainer`
- **Margins** (with axis labels): `{ top: 5, right: 20, bottom: 25, left: 10 }`
- **Margins** (without axis labels): `{ top: 5, right: 20, bottom: 5, left: 10 }`

### Color Palette

```typescript
const COLORS = ["#2563eb", "#dc2626", "#16a34a", "#9333ea", "#ea580c"];
//               blue        red        green      purple     orange
```

- Primary single-series color: `#2563eb`
- Multi-series: index into `COLORS[idx % COLORS.length]`
- Reference lines / guides: `#9ca3af` (gray-400)

### Grid and Axes

```tsx
<CartesianGrid strokeDasharray="3 3" />
```

**Numeric 0–1 axis** (probabilities, rates):

```tsx
<XAxis
    dataKey="fieldName"
    type="number"
    domain={[0, 1]}
    label={{ value: "Axis Label", position: "insideBottom", offset: -15 }}
/>
<YAxis
    domain={[0, 1]}
    label={{ value: "Axis Label", angle: -90, position: "insideLeft" }}
/>
```

**Categorical axis** (metric names, categories):

```tsx
<XAxis dataKey="category" />
<YAxis domain={[0, 1]} />
```

### Tooltip

Standard formatter for numeric values:

```tsx
<Tooltip formatter={(value: number | undefined) => value?.toFixed(4) ?? ""} />
```

With custom label:

```tsx
<Tooltip
    formatter={(value: number | undefined) => value?.toFixed(4) ?? ""}
    labelFormatter={(label) => `Label: ${Number(label).toFixed(4)}`}
/>
```

### Line Styling

```tsx
<Line
    name="Series Label"
    type="monotone"
    dataKey="fieldName"
    stroke="#2563eb"
    dot={false}           // false for dense data, { r: 4 } for sparse
    strokeWidth={2}
/>
```

### Reference Lines (diagonal, threshold markers)

```tsx
<ReferenceLine
    segment={[{ x: 0, y: 0 }, { x: 1, y: 1 }]}
    stroke="#9ca3af"
    strokeDasharray="5 5"
    label="Random"
/>
```

### Data Transformation

Transform parallel arrays into Recharts point objects:

```tsx
// Input: { fpr: number[], tpr: number[] }
const chartData = data.fpr.map((fpr, i) => ({
    fpr,
    tpr: data.tpr[i],
}));
```

Pivot models into comparison data:

```tsx
// Input: models[] with metric fields
const chartData = metrics.map((metric) => {
    const point: Record<string, string | number> = { metric: labels[metric] };
    for (const model of models) {
        point[model.name] = Number(model[metric].toFixed(4));
    }
    return point;
});
```

### Multi-Series (Dynamic)

```tsx
{items.map((item, idx) => (
    <Line
        key={item.label}
        name={item.label}
        dataKey="y"
        stroke={item.color || COLORS[idx % COLORS.length]}
        dot={false}
        strokeWidth={2}
    />
))}
```

## Checklist

- [ ] `"use client"` directive at top of file
- [ ] Props interface defined with proper types
- [ ] `ResponsiveContainer` wrapping with `width="100%"` and `height={350}`
- [ ] `CartesianGrid strokeDasharray="3 3"`
- [ ] Axes with labels (if applicable) using project conventions
- [ ] Tooltip with `.toFixed(4)` formatter
- [ ] Uses project color palette (`COLORS` array or `#2563eb` primary)
- [ ] Data type added to `apps/web/lib/types.ts` (if new)
- [ ] Component exported as named export
- [ ] Integrated into page wrapped in `<Card>`
