import math
from js import document
from pyodide.ffi.wrappers import add_event_listener

# ===== キャンバス取得 =====
off_canvas = document.getElementById("offscreen")
off_ctx = off_canvas.getContext("2d")

view_canvas = document.getElementById("view")
view_ctx = view_canvas.getContext("2d")

vw = off_canvas.width      # 4000
vh = off_canvas.height     # 400

view_w = view_canvas.width
view_h = view_canvas.height

# ===== 仮想キャンバスに sin カーブを描画（1回だけ） =====

def draw_offscreen():
    # 背景
    off_ctx.fillStyle = "white"
    off_ctx.fillRect(0, 0, vw, vh)

    # 軸
    off_ctx.strokeStyle = "#cccccc"
    off_ctx.lineWidth = 1

    # x 軸
    off_ctx.beginPath()
    off_ctx.moveTo(0, vh / 2)
    off_ctx.lineTo(vw, vh / 2)
    off_ctx.stroke()

    # y 軸（左）
    off_ctx.beginPath()
    off_ctx.moveTo(0, 0)
    off_ctx.lineTo(0, vh)
    off_ctx.stroke()

    # sin カーブ
    off_ctx.strokeStyle = "blue"
    off_ctx.lineWidth = 2

    off_ctx.beginPath()

    x_min = 0.0
    x_max = 4 * math.pi

    for i in range(vw + 1):
        t = i / vw
        x = x_min + (x_max - x_min) * t
        y = math.sin(x)

        canvas_x = i
        canvas_y = vh / 2 - y * (vh / 2 - 20)

        if i == 0:
            off_ctx.moveTo(canvas_x, canvas_y)
        else:
            off_ctx.lineTo(canvas_x, canvas_y)

    off_ctx.stroke()

# ===== スクロール状態管理 =====
scroll_x = 0
is_dragging = False
last_mouse_x = 0

def redraw():
    global scroll_x

    # 範囲チェック
    if scroll_x < 0:
        scroll_x = 0
    if scroll_x > vw - view_w:
        scroll_x = vw - view_w

    view_ctx.clearRect(0, 0, view_w, view_h)

    view_ctx.drawImage(
        off_canvas,
        scroll_x, 0, view_w, vh,   # 仮想キャンバス側
        0, 0, view_w, view_h       # 表示側
    )

# ===== マウスイベント =====
def on_mousedown(event):
    global is_dragging, last_mouse_x
    is_dragging = True
    last_mouse_x = event.offsetX  # キャンバス内の X 座標

def on_mousemove(event):
    global is_dragging, last_mouse_x, scroll_x
    if not is_dragging:
        return

    current_x = event.offsetX
    dx = current_x - last_mouse_x

    # 右ドラッグで右方向を見るように
    scroll_x -= dx
    last_mouse_x = current_x

    redraw()

def on_mouseup(event):
    global is_dragging
    is_dragging = False

def on_mouseleave(event):
    global is_dragging
    is_dragging = False

# ===== 初期化処理 =====
def init():
    draw_offscreen()
    redraw()

    # wrappers.add_event_listener を使うと create_proxy を意識せずに済む
    add_event_listener(view_canvas, "mousedown", on_mousedown)
    add_event_listener(view_canvas, "mousemove", on_mousemove)
    add_event_listener(view_canvas, "mouseup", on_mouseup)
    add_event_listener(view_canvas, "mouseleave", on_mouseleave)

# スクリプト読み込み時に初期化
init()