"""Build the offline travel SVG include from public-domain Natural Earth land data."""
import json, math
from pathlib import Path
root = Path(__file__).resolve().parents[2]
data = json.loads((root / 'assets/data/world-land-110m.geojson').read_text())

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
'<svg class="travel-map__canvas" viewBox="0 0 720 370" role="img" aria-label="Visited countries: South Korea, Malaysia, France, Spain. 去过的国家：韩国、马来西亚、法国、西班牙。">',
'<title>World travel map · 世界足迹</title>',
'<g class="travel-map__graticule" aria-hidden="true">']
for lat in [-60,-30,0,30,60]:
    svg.append(f'<path d="{path([[lon,lat] for lon in range(-180,181,5)],False)}"/>')
for lon in [-120,-60,0,60,120]:
    svg.append(f'<path d="{path([[lon,lat] for lat in range(-90,91,5)],False)}"/>')
svg.append('</g><g class="travel-map__land" aria-hidden="true">')
svg.extend(f'<path d="{p}"/>' for p in paths)
svg.append('</g>')
# Approximate country-level reference positions; these do not imply any city visited.
for en,zh,lon,lat,dx,dy in [('South Korea','韩国',127.8,36.3,12,-11),('Malaysia','马来西亚',102.0,4.5,12,20),('France','法国',2.4,46.6,10,-14),('Spain','西班牙',-3.5,40.2,-12,22)]:
    x,y=project([lon,lat]); anchor='end' if dx<0 else 'start'
    svg.append(f'<g class="travel-map__point" tabindex="0" role="img" aria-label="{en} · {zh}" transform="translate({x:.1f} {y:.1f})"><title>{en} · {zh}</title><circle class="travel-map__halo" r="7.8"/><circle class="travel-map__dot" r="4.8"/><text class="travel-map__label" x="{dx}" y="{dy}" text-anchor="{anchor}" data-lang="en">{en}</text><text class="travel-map__label" x="{dx}" y="{dy}" text-anchor="{anchor}" data-lang="zh">{zh}</text></g>')
svg.extend(['</svg>',
'<p class="travel-map__legend"><span class="travel-map__key" aria-hidden="true"></span><span data-lang="en">South Korea · Malaysia · France · Spain</span><span data-lang="zh">韩国 · 马来西亚 · 法国 · 西班牙</span></p>',
'<p class="travel-map__note"><span data-lang="en">Country-level markers</span><span data-lang="zh">以国家为单位标记</span> · <a href="https://www.naturalearthdata.com/" target="_blank" rel="noopener">Natural Earth</a></p>',
'</section>'])
(root/'_includes/travel-map.html').write_text('\n'.join(svg)+'\n')
print(f'Generated {root / "_includes/travel-map.html"} ({sum(map(len,svg))} characters)')
