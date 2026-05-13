from PIL import Image, ImageDraw

W, H = 1024, 576
UNIT = 80

# Geometry (checker diameter = 1 unit)
POINT_BASE = 1.0
POINT_HEIGHT = 5.05
OPPOSITE_GAP = 0.75
BAR_WIDTH = 1.0625
FRAME = 0.5

SUB_BOARD_W = 6.0  # 6 points
INNER_W = 2 * SUB_BOARD_W + BAR_WIDTH  # 13.2
INNER_H = 2 * POINT_HEIGHT + OPPOSITE_GAP  # 10.85

OUTER_W = INNER_W + 2 * FRAME
OUTER_H = INNER_H + 2 * FRAME

# Colors
bg_color = (20, 20, 20)
frame_color = (100, 70, 40)
board_color = (140, 95, 55)
bar_color = (110, 80, 45)
color_light = (210, 180, 140)
color_dark = (40, 40, 40)

def generate_board(canvas_size):
    W, H = canvas_size
    scale = min(W / OUTER_W, H / OUTER_H)
    
    px_frame = FRAME * scale
    px_bar_w = BAR_WIDTH * scale
    px_point_base = POINT_BASE * scale
    px_point_h = POINT_HEIGHT * scale
    
    offset_x = (W - INNER_W * scale - 2 * px_frame) / 2
    offset_y = (H - INNER_H * scale - 2 * px_frame) / 2
    
    board_left = offset_x + px_frame
    board_top = offset_y + px_frame
    board_right = board_left + INNER_W * scale
    board_bottom = board_top + INNER_H * scale
    bar_left = board_left + SUB_BOARD_W * scale
    bar_right = bar_left + px_bar_w
    
    img = Image.new('RGB', (W, H), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Frame + board + bar
    draw.rectangle([offset_x, offset_y, offset_x + INNER_W * scale + 2 * px_frame,
                    offset_y + INNER_H * scale + 2 * px_frame], fill=frame_color)
    draw.rectangle([board_left, board_top, board_right, board_bottom], fill=board_color)
    draw.rectangle([bar_left, board_top, bar_right, board_bottom], fill=bar_color)
    
    def draw_top_points(left, right, base_y, colors):
        arr = colors
        for i in range(6):
            x1 = left + i * px_point_base
            x2 = left + (i + 1) * px_point_base
            xm = (x1 + x2) / 2
            draw.polygon([(x1, base_y), (x2, base_y), (xm, base_y + px_point_h)], fill=arr[i % 2])
    
    def draw_bottom_points(left, right, base_y, colors):
        arr = colors
        for i in range(6):
            x1 = left + i * px_point_base
            x2 = left + (i + 1) * px_point_base
            xm = (x1 + x2) / 2
            draw.polygon([(x1, base_y), (x2, base_y), (xm, base_y - px_point_h)], fill=arr[i % 2])
    
    # CRITICAL FIX: top and bottom use DIFFERENT color alternations so opposing points differ
    # Left side: top starts with dark, bar-adjacent = light
    # Left side: bottom must start with light, bar-adjacent = dark (so corresponding x-positions are opposite)
    left_top_colors = [color_dark, color_light]
    left_bottom_colors = [color_light, color_dark]
    
    # Right side: top starts with light, bar-adjacent = dark
    # Right side: bottom starts with dark, bar-adjacent = light
    right_top_colors = [color_light, color_dark]
    right_bottom_colors = [color_dark, color_light]
    
    # Upper sub-boards (top long side, points point down)
    draw_top_points(board_left, bar_left, board_top, left_top_colors)       # upper-left
    draw_top_points(bar_right, board_right, board_top, right_top_colors)      # upper-right
    
    # Lower sub-boards (bottom long side, points point up)
    draw_bottom_points(board_left, bar_left, board_bottom, left_bottom_colors)    # lower-left
    draw_bottom_points(bar_right, board_right, board_bottom, right_bottom_colors)  # lower-right
    
    return img

landscape = generate_board((1024, 576))
landscape.save("/Users/prh/Developer/huffmanwrites/static/img/articles/sb-landscape-v5.png")

print("Saved: sb-landscape-v5.png")
