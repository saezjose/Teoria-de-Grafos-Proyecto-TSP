import traceback
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

try:
    import contextily as ctx
except Exception as e:
    print('contextily import failed:', e)
    raise


def ll2xy(lat, lon):
    k = 6378137
    x = lon * (k * math.pi / 180.0)
    y = math.log(math.tan((90 + lat) * math.pi / 360.0)) * k
    return x, y

coords = [(40.4168, -3.7038), (41.3851, 2.1734)]  # Madrid, Barcelona
xs = [ll2xy(lat, lon)[0] for lat, lon in coords]
ys = [ll2xy(lat, lon)[1] for lat, lon in coords]

fig, ax = plt.subplots(figsize=(6, 4))
ax.scatter(xs, ys, c='red', zorder=10)

try:
    ctx.add_basemap(ax, source=ctx.providers.CartoDB.DarkMatter, zoom_adjust=0)
    print('add_basemap OK')
except Exception:
    traceback.print_exc()

plt.close(fig)
