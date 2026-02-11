import math
from js import document, window
from pyodide import create_proxy

# ===== キャンバス取得 =====
off_canvas = document.getElementById("offscreen")
off_ctx = off_canvas.getContext("2d")

view_canvas = document.getElementById("view")
view_ctx = view_canvas.getContext("2d")

vw = off_canvas.width      # 4000
vh = off_canvas.height     # 400

# ===== 仮想キャンバスに sin カーブを描画（1回だけ） =====

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

# ===== スクロール状態管理用の変数 =====

# 仮想キャンバス上の表示開始位置（sx）
scroll_x = 0

# ドラッグ中かどうか
is_dragging = False

# 最後のマウス位置
last_mouse_x = 0

# 物理キャンバスの幅
view_w = view_canvas.width
view_h = view_canvas.height

# ===== 描画関数（現在の scroll_x に基づいて転送） =====

def redraw():
    global scroll_x
    # 範囲チェック（オーバースクロール防止）
    if scroll_x < 0:
        scroll_x = 0
    if scroll_x > vw - view_w:
        scroll_x = vw - view_w

    # 物理キャンバスをクリア
    view_ctx.clearRect(0, 0, view_w, view_h)

    # 仮想キャンバスの scroll_x〜scroll_x+view_w を表示側に描画
    view_ctx.drawImage(
        off_canvas,
        scroll_x, 0, view_w, vh,    # 仮想キャンバス側
        0, 0, view_w, view_h        # 物理キャンバス側
    )

# 初回描画
redraw()

# ===== マウスイベントハンドラ =====

def on_mousedown(event):
    global is_dragging, last_mouse_x
    is_dragging = True
    # キャンバス内での X 座標（offsetX を使うと楽）
    last_mouse_x = event.offsetX

def on_mousemove(event):
    global is_dragging, last_mouse_x, scroll_x
    if not is_dragging:
        return

    # 現在の位置
    current_x = event.offsetX
    dx = current_x - last_mouse_x

    # 右にドラッグしたら左側に戻るようにしたいので、scroll_x をマイナス方向に動かす
    scroll_x -= dx

    last_mouse_x = current_x

    redraw()

def on_mouseup(event):
    global is_dragging
    is_dragging = False

def on_mouseleave(event):
    # キャンバス外に出たときもドラッグ終了にする
    global is_dragging
    is_dragging = False

# ===== イベントリスナ登録（PyScript / Pyodide 用） =====

# Python 関数を JS コールバック用にラップ
mousedown_proxy = create_proxy(on_mousedown)
mousemove_proxy = create_proxy(on_mousemove)
mouseup_proxy = create_proxy(on_mouseup)
mouseleave_proxy = create_proxy(on_mouseleave)

view_canvas.addEventListener("mousedown", mousedown_proxy)
view_canvas.addEventListener("mousemove", mousemove_proxy)
view_canvas.addEventListener("mouseup", mouseup_proxy)
view_canvas.addEventListener("mouseleave", mouseleave_proxy)