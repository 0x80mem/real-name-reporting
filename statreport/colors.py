import numpy as np

from colorsys import rgb_to_hls, hls_to_rgb

def rgb_to_hsl(rgb):
    r, g, b = rgb
    h, l, s = rgb_to_hls(r, g, b)
    return (h * 360, s, l)

def hsl_to_rgb(hsl):
    h, s, l = hsl
    h = h / 360.0
    return hls_to_rgb(h, l, s)


colors = [[46, 44, 105], [70, 73, 156], [142, 141, 200], [216, 163, 152], [247, 226, 219], [250, 245, 240]]
colors = np.array(colors) / 255

def expand_colors():
    new_colors = np.zeros((len(colors) * 2 - 1, 3))
    for i in range(len(colors) - 1):
        new_colors[i * 2] = colors[i]
        new_colors[i * 2 + 1] = (colors[i] + colors[i + 1]) / 2
    new_colors[-1] = colors[-1]
    return new_colors

def generate_monochromatic_colors(base_colors, n):
    new_colors = np.zeros((n, 3))
    for i in range(n):
        bais = i // len(base_colors) 
        bais = bais * ((-1) ** bais // 2)
        bais = bais // 2

        h, s, l = rgb_to_hsl(base_colors[i % len(base_colors)])
        h = h + 20 * bais
        s = max(0, min(1, s + 0.1 * bais))
        l = max(0, min(1, l + 0.1 * bais))
        new_colors[i] = hsl_to_rgb((h, s, l))
    return new_colors

# 生成渐变色
def get_colors(n):
    if n <= len(colors):
        return colors[:n]
    else:
        ex_colors = expand_colors()
        if n <= len(ex_colors):
            return ex_colors[:n]
        else:
            return generate_monochromatic_colors(ex_colors, n)
        
def random_color_func(word, font_size, position, orientation, font_path, random_state):
    ex_colors = expand_colors()
    dark_colors = [color for color in ex_colors if color.mean() < 0.9]
    dark_colors = dark_colors[random_state.randint(0, len(dark_colors) - 1)]
    return f"rgb{tuple(map(int, dark_colors * 255))}"