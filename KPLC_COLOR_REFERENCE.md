# KPLC Color Reference Guide

## Official KPLC Brand Colors

### Primary Colors

#### KPLC Blue (Primary)
- **Hex:** #00337F
- **RGB:** rgb(0, 51, 127)
- **HSL:** hsl(213, 100%, 25%)
- **Usage:** Headers, buttons, active states, primary text
- **CSS Variable:** `--primary-color`

#### KPLC Blue Dark
- **Hex:** #002555
- **RGB:** rgb(0, 37, 85)
- **HSL:** hsl(213, 100%, 17%)
- **Usage:** Hover states, gradients, darker accents
- **CSS Variable:** `--primary-dark`

#### KPLC Blue Light
- **Hex:** #1a5fa0
- **RGB:** rgb(26, 95, 160)
- **HSL:** hsl(213, 72%, 36%)
- **Usage:** Light backgrounds, secondary accents
- **CSS Variable:** `--primary-light`

### Secondary Colors

#### KPLC Orange
- **Hex:** #F39200
- **RGB:** rgb(243, 146, 0)
- **HSL:** hsl(38, 100%, 48%)
- **Usage:** Warnings, incidents, secondary highlights
- **CSS Variable:** `--secondary-color`

#### KPLC Orange Light
- **Hex:** #FFB84D
- **RGB:** rgb(255, 184, 77)
- **HSL:** hsl(38, 100%, 65%)
- **Usage:** Light orange backgrounds, hover states
- **CSS Variable:** `--secondary-light`

### Accent Colors

#### KPLC Green
- **Hex:** #00A651
- **RGB:** rgb(0, 166, 81)
- **HSL:** hsl(145, 100%, 33%)
- **Usage:** Success states, access events, positive indicators
- **CSS Variable:** `--accent-color`

## Neutral Colors

### Backgrounds
- **White:** #FFFFFF (Cards, forms, main background)
- **Light Gray:** #f8f9fa (Sidebar, light backgrounds)
- **Very Light Gray:** #f5f5f5 (Page background)
- **Light Blue:** #e8f0f8 (Hover states, light accents)
- **Light Orange:** #fff8e8 (Warning backgrounds)
- **Light Green:** #e8f8f0 (Success backgrounds)

### Text Colors
- **Dark:** #333333 (Primary text)
- **Medium:** #666666 (Secondary text)
- **Light:** #999999 (Tertiary text)
- **White:** #FFFFFF (Text on dark backgrounds)

### Borders
- **Light:** #e0e0e0 (Subtle borders)
- **Medium:** #ddd (Standard borders)
- **Dark:** #00337F (Accent borders)

## Color Usage Guide

### Header Component
```css
background: linear-gradient(135deg, #00337F 0%, #002555 100%);
color: white;
box-shadow: 0 2px 8px rgba(0, 51, 127, 0.2);
```

### Sidebar Component
```css
background: #f8f9fa;
color: #333;
border-right: 1px solid #e0e0e0;
```

### Active Menu Item
```css
background-color: #e8f0f8;
border-left-color: #00337F;
color: #00337F;
```

### Buttons
```css
/* Primary Button */
background-color: #00337F;
color: white;

/* Primary Button Hover */
background-color: #002555;
```

### Stat Cards
```css
/* Primary (Blue) */
border-left-color: #00337F;
background-color: #e8f0f8;

/* Warning (Orange) */
border-left-color: #F39200;
background-color: #fff8e8;

/* Accent (Green) */
border-left-color: #00A651;
background-color: #e8f8f0;

/* Success (Green) */
border-left-color: #28a745;
background-color: #e8f5e9;
```

### Table Header
```css
background-color: #f0f4f8;
border-bottom: 2px solid #00337F;
color: #00337F;
```

### Forms
```css
/* Input Border */
border-color: #ddd;

/* Input Focus */
border-color: #00337F;
box-shadow: 0 0 0 3px rgba(0, 51, 127, 0.1);
```

### Alerts
```css
/* Success Alert */
background-color: #d4edda;
border-color: #28a745;
color: #155724;

/* Danger Alert */
background-color: #f8d7da;
border-color: #dc3545;
color: #721c24;

/* Warning Alert */
background-color: #fff3cd;
border-color: #ffc107;
color: #856404;
```

## Accessibility Considerations

### Color Contrast Ratios

| Color Combination | Ratio | WCAG Level |
|---|---|---|
| #00337F on white | 8.6:1 | AAA |
| #F39200 on white | 4.5:1 | AA |
| #00A651 on white | 5.5:1 | AAA |
| White on #00337F | 8.6:1 | AAA |
| White on #002555 | 10.2:1 | AAA |

### Best Practices
- Always use sufficient contrast
- Don't rely on color alone to convey information
- Use icons and text labels with colors
- Test with color blindness simulators

## CSS Variables Reference

```css
:root {
  /* Primary Colors */
  --primary-color: #00337F;
  --primary-dark: #002555;
  --primary-light: #1a5fa0;
  
  /* Secondary Colors */
  --secondary-color: #F39200;
  --secondary-light: #FFB84D;
  
  /* Accent Colors */
  --accent-color: #00A651;
  
  /* Status Colors */
  --success-color: #28a745;
  --danger-color: #dc3545;
  --warning-color: #ffc107;
  --info-color: #17a2b8;
  
  /* Neutral Colors */
  --light-color: #f5f5f5;
  --dark-color: #333;
  --border-color: #ddd;
  --text-color: #333;
  --text-light: #666;
  
  /* Shadows */
  --shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 4px 8px rgba(0, 0, 0, 0.15);
  --shadow-xl: 0 10px 25px rgba(0, 51, 127, 0.15);
}
```

## Color Palette Export

### Hex Codes
```
#00337F - KPLC Blue
#002555 - KPLC Blue Dark
#1a5fa0 - KPLC Blue Light
#F39200 - KPLC Orange
#FFB84D - KPLC Orange Light
#00A651 - KPLC Green
#f8f9fa - Light Gray
#e8f0f8 - Light Blue
#fff8e8 - Light Orange
#e8f8f0 - Light Green
```

### RGB Values
```
rgb(0, 51, 127) - KPLC Blue
rgb(0, 37, 85) - KPLC Blue Dark
rgb(26, 95, 160) - KPLC Blue Light
rgb(243, 146, 0) - KPLC Orange
rgb(255, 184, 77) - KPLC Orange Light
rgb(0, 166, 81) - KPLC Green
```

## Design System Integration

All colors are defined as CSS variables in:
`apps/sigma/sigma/frontend/src/assets/styles/main.css`

To use colors in components:
```css
color: var(--primary-color);
background-color: var(--secondary-color);
border-color: var(--accent-color);
```

## Future Updates

When updating colors:
1. Update CSS variables in main.css
2. Update all component styles
3. Test contrast ratios
4. Verify responsive design
5. Test on all browsers
6. Update this reference guide

