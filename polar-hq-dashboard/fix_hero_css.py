import re

with open('src/index.css', 'r', encoding='utf-8') as f:
    css = f.read()

new_hero_css = """/* --- Hero Banner --- */
.hero-banner {
  background: linear-gradient(to right, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.6) 40%, rgba(255,255,255,0.2) 100%), url('/bg-station.jpg') center/cover;
  padding: 1.5rem 2.5rem;
  color: var(--ncpor-navy);
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1.5px solid var(--border-color);
}

.hero-banner h2 {
  font-size: 1.8rem;
  margin-bottom: 0.25rem;
  font-weight: 700;
  text-shadow: 0 1px 2px rgba(255,255,255,0.8);
}

.hero-banner p {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 500;
  opacity: 0.9;
  color: var(--text-primary);
  text-shadow: 0 1px 2px rgba(255,255,255,0.8);
}

.hero-quote {
  font-style: italic;
  font-weight: 600;
  opacity: 1;
  text-align: right;
  max-width: 300px;
  color: var(--ncpor-navy);
  text-shadow: 0 1px 2px rgba(255,255,255,0.8);
}

[data-theme="dark"] .hero-banner {
  background: linear-gradient(to right, rgba(15,23,42,0.9) 0%, rgba(15,23,42,0.7) 50%, rgba(15,23,42,0.4) 100%), url('/bg-station.jpg') center/cover;
  color: #f1f5f9;
}
[data-theme="dark"] .hero-banner p { color: #cbd5e1; text-shadow: none; }
[data-theme="dark"] .hero-banner h2 { color: #f1f5f9; text-shadow: none; }
[data-theme="dark"] .hero-quote { color: #f1f5f9; text-shadow: none; }
"""

css = re.sub(r'/\* --- Hero Banner --- \*/.*?/\* --- Control Bar --- \*/', new_hero_css + '\n/* --- Control Bar --- */', css, flags=re.DOTALL)

with open('src/index.css', 'w', encoding='utf-8') as f:
    f.write(css)
