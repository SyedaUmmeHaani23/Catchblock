"""A self-contained health badge (SVG) a project can commit and show in its README. No external service."""
COLORS = {"green": "#2ea36f", "amber": "#d29922", "red": "#e5484d"}

def badge_svg(score: int, verdict: str) -> str:
    label, value = "catchblock", f"{int(score)}/100"
    lw, vw = 7 * len(label) + 14, 7 * len(value) + 14
    w, color = lw + vw, COLORS.get(verdict, COLORS["red"])
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="20" role="img" aria-label="{label}: {value}">'
            f'<rect width="{lw}" height="20" rx="3" fill="#24292f"/><rect x="{lw}" width="{vw}" height="20" rx="3" fill="{color}"/>'
            f'<rect x="{lw}" width="6" height="20" fill="{color}"/>'
            f'<g fill="#fff" font-family="Verdana,DejaVu Sans,sans-serif" font-size="11" text-anchor="middle">'
            f'<text x="{lw / 2}" y="14">{label}</text><text x="{lw + vw / 2}" y="14" font-weight="bold">{value}</text></g></svg>')
