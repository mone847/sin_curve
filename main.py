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

# ===== 周波数関連のパラメータ =====
base_cycles = 4.0          # 基本の周期数
freq_factor = 1.0          # 周波数倍率（1.0 が基準）

# ===== スクロール状態管理 =====
scroll_x = 0
is_dragging = False
last_mouse_x = 0
start_mouse_y = 0
start_freq_factor = 1.0

def draw_offscreen():
    """現在の freq_factor を使って仮想キャンバスに sin カーブを描く"""
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
    # freq_factor をかけて周期数を変える
    x_max = base_cycles * freq_factor * math.pi * 2.0

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

def redraw_view():
    """現在の scroll_x に基づいて物理キャンバスに転送"""
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

# ===== マウスドラッグによるスクロール＆周期変更 =====
def on_mousedown(event):
    global is_dragging, last_mouse_x, start_mouse_y, start_freq_factor
    is_dragging = True
    last_mouse_x = event.offsetX
    start_mouse_y = event.offsetY
    start_freq_factor = freq_factor

def on_mousemove(event):
    global is_dragging, last_mouse_x, scroll_x, freq_factor

    if not is_dragging:
        return

    current_x = event.offsetX
    current_y = event.offsetY

    # 左右ドラッグ → スクロール
    dx = current_x - last_mouse_x
    scroll_x -= dx
    last_mouse_x = current_x

    # 上下ドラッグ → 周期変更
    dy = current_y - start_mouse_y  # 下方向が正

    # 感度調整
    scale = 0.0125

    new_factor = start_freq_factor * (1.0 + -dy * scale)

    # クリップ
    if new_factor < 0.2:
        new_factor = 0.2
    if new_factor > 5.0:
        new_factor = 5.0

    freq_factor = new_factor

    draw_offscreen()
    redraw_view()

def on_mouseup(event):
    global is_dragging
    is_dragging = False

def on_mouseleave(event):
    global is_dragging
    is_dragging = False

# ===== ホイールでの周期変更 =====
def on_wheel(event):
    global freq_factor

    # ページのスクロールを抑止
    event.preventDefault()

    # event.deltaY > 0 なら「下に」スクロール（一般的なマウス）[web:86][web:92]
    # 符号を反転して「上スクロールで周波数アップ」にする
    delta = -event.deltaY

    # 感度調整
    wheel_scale = 0.001

    # delta が正なら freq_factor を増やす、負なら減らす
    new_factor = freq_factor * (1.0 + delta * wheel_scale)

    # クリップ
    if new_factor < 0.2:
        new_factor = 0.2
    if new_factor > 5.0:
        new_factor = 5.0

    freq_factor = new_factor

    draw_offscreen()
    redraw_view()

# ===== 初期化処理 =====
def init():
    draw_offscreen()
    redraw_view()

    add_event_listener(view_canvas, "mousedown", on_mousedown)
    add_event_listener(view_canvas, "mousemove", on_mousemove)
    add_event_listener(view_canvas, "mouseup", on_mouseup)
    add_event_listener(view_canvas, "mouseleave", on_mouseleave)

    # wheel イベントをキャンバスに登録（パッシブ false にして preventDefault を効かせる）[web:86][web:92]
    add_event_listener(view_canvas, "wheel", on_wheel, options={"passive": False})

init()