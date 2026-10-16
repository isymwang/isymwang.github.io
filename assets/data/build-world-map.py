"""Build the offline travel SVG include from public-domain Natural Earth land data."""
import json, math
from pathlib import Path
root = Path(__file__).resolve().parents[2]
data = json.loads((root / 'assets/data/world-land-110m.geojson').read_text())
# City, country, Chinese city/country, conference, longitude, latitude, label offset.
visits = [
    ('Kuala Lumpur', 'Malaysia', '吉隆坡', '马来西亚', 'ICIP 2023', 101.6869, 3.139, -12, 20),
    ('Seoul', 'South Korea', '首尔', '韩国', 'ICASSP 2024', 126.978, 37.5665, 12, -11),
    ('Nantes', 'France', '南特', '法国', 'ICME 2025', -1.5536, 47.2184, 10, -14),
    ('Barcelona', 'Spain', '巴塞罗那', '西班牙', 'ICASSP 2026', 2.1734, 41.3851, -12, 22),
]
visited_en = '; '.join(f'{city}, {country} ({conference})' for city, country, _, _, conference, *_ in visits)
visited_zh = '、'.join(f'{country}{city}（{conference}）' for _, _, city, country, conference, *_ in visits)

def project(pair):
    # Natural Earth I projection (Tom Patterson / Bojan Savric), radians.
    lon, lat = [math.radians(v) for v in pair[:2]]
    p2 = lat * lat
    p4 = p2 * p2
    x = lon * (0.8707 - 0.131979*p2 + p4*(-0.013791 + p4*(0.003971*p2 - 0.001529*p4)))
    y = lat * (1.007226 + p2*(0.015085 + p4*(-0.044475 + 0.028874*p2 - 0.005916*p4)))
    return (360 + x*127, 185 - y*127)

def simplify(points, tolerance=.47):
    if len(points) < 4: return points
    first,last=points[0],points[-1]
    dx,dy=last[0]-first[0],last[1]-first[1]
    length=dx*dx+dy*dy
    dmax,index=0,0
    for i,p in enumerate(points[1:-1],1):
        t=max(0,min(1,((p[0]-first[0])*dx+(p[1]-first[1])*dy)/length)) if length else 0
        d=math.hypot(p[0]-first[0]-t*dx,p[1]-first[1]-t*dy)
        if d>dmax: dmax,index=d,i
    if dmax>tolerance:
        return simplify(points[:index+1],tolerance)[:-1]+simplify(points[index:],tolerance)
    return [first,last]

def path(coords, closed=True):
    pts=simplify([project(p) for p in coords])
    return 'M'+'L'.join(f'{x:.1f},{y:.1f}' for x,y in pts)+('Z' if closed else '')
paths=[]
for f in data['features']:
    g=f['geometry']
    polys=g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]
    for poly in polys:
        paths.append(''.join(path(ring) for ring in poly))
svg=['<section class="travel-map" id="travels" aria-labelledby="travel-map-title">',
'<h2 id="travel-map-title"><span data-lang="en">Around the world</span><span data-lang="zh">我的足迹</span></h2>',
f'<svg class="travel-map__canvas" viewBox="0 0 720 370" role="img" aria-label="Conference visits: {visited_en}. 参会城市：{visited_zh}。">',
'<title>World travel map · 世界足迹</title>',
'<g class="travel-map__graticule" aria-hidden="true">']
for lat in [-60,-30,0,30,60]:
    svg.append(f'<path d="{path([[lon,lat] for lon in range(-180,181,5)],False)}"/>')
for lon in [-120,-60,0,60,120]:
    svg.append(f'<path d="{path([[lon,lat] for lat in range(-90,91,5)],False)}"/>')
svg.append('</g><g class="travel-map__land" aria-hidden="true">')
svg.extend(f'<path d="{p}"/>' for p in paths)
svg.append('</g>')
# Approximate city-center positions, using the same projection as the coastline.
for city,country,city_zh,country_zh,conference,lon,lat,dx,dy in visits:
    x,y=project([lon,lat]); anchor='end' if dx<0 else 'start'
    description=f'{city}, {country} ({conference}) · {country_zh}{city_zh}（{conference}）'
    svg.append(f'<g class="travel-map__point" tabindex="0" role="img" aria-label="{description}" transform="translate({x:.1f} {y:.1f})"><title>{description}</title><circle class="travel-map__halo" r="7.8"/><circle class="travel-map__dot" r="4.8"/><text class="travel-map__label" x="{dx}" y="{dy}" text-anchor="{anchor}" data-lang="en">{city}</text><text class="travel-map__label" x="{dx}" y="{dy}" text-anchor="{anchor}" data-lang="zh">{city_zh}</text></g>')
legend_en = ' · '.join(f'<span class="travel-map__visit">{city}, {country} <span class="travel-map__conference">({conference})</span></span>' for city, country, _, _, conference, *_ in visits)
legend_zh = ' · '.join(f'<span class="travel-map__visit">{country}{city}<span class="travel-map__conference">（{conference}）</span></span>' for _, _, city, country, conference, *_ in visits)
svg.extend(['</svg>',
f'<p class="travel-map__legend"><span class="travel-map__key" aria-hidden="true"></span><span data-lang="en">{legend_en}</span><span data-lang="zh">{legend_zh}</span></p>',
'<p class="travel-map__note"><span data-lang="en">Conference cities</span><span data-lang="zh">参会城市</span> · <a href="https://www.naturalearthdata.com/" target="_blank" rel="noopener">Natural Earth</a></p>',
'</section>'])
(root/'_includes/travel-map.html').write_text('\n'.join(svg)+'\n')
print(f'Generated {root / "_includes/travel-map.html"} ({sum(map(len,svg))} characters)')
