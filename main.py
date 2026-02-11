import math
from js import document

# 仮想キャンバス（大きな領域）
off_canvas = document.getElementById("offscreen")
off_ctx = off_canvas.getContext("2d")

# 物理キャンバス（表示領域）
view_canvas = document.getElementById("view")
view_ctx = view_canvas.getContext("2d")

# 仮想キャンバスのサイズ
vw = off_canvas.width      # 4000
vh = off_canvas.height     # 400

# 背景を白で塗る
off_ctx.fillStyle = "white"
off_ctx.fillRect(0, 0, vw, vh)

# 軸の描画
off_ctx.strokeStyle = "#cccccc"
off_ctx.lineWidth = 1

# x 軸（中央）
off_ctx.beginPath()
off_ctx.moveTo(0, vh / 2)
off_ctx.lineTo(vw, vh / 2)
off_ctx.stroke()

# y 軸（左）
off_ctx.beginPath()
off_ctx.moveTo(0, 0)
off_ctx.lineTo(0, vh)
off_ctx.stroke()

# sin カーブを仮想キャンバスに描画
off_ctx.strokeStyle = "blue"
off_ctx.lineWidth = 2

off_ctx.beginPath()

# x: 0〜 4π を 0〜vw に対応させる例
x_min = 0.0
x_max = 4 * math.pi

for i in range(vw + 1):
    # キャンバス座標 → 数学座標
    t = i / vw
    x = x_min + (x_max - x_min) * t
    y = math.sin(x)

    # y = -1〜1 を キャンバス高さに変換（中央が 0）
    canvas_x = i
    canvas_y = vh / 2 - y * (vh / 2 - 20)  # 上下に少し余白を持たせる

    if i == 0:
        off_ctx.moveTo(canvas_x, canvas_y)
    else:
        off_ctx.lineTo(canvas_x, canvas_y)

off_ctx.stroke()

# ===== 仮想キャンバス → 物理キャンバスに転送 =====

# 物理キャンバスをクリア
view_ctx.clearRect(0, 0, view_canvas.width, view_canvas.height)

# drawImage で縮小して転送
#   引数: (画像, sx, sy, sWidth, sHeight, dx, dy, dWidth, dHeight)
view_ctx.drawImage(
    off_canvas,
    0, 0, vw, vh,                      # 仮想キャンバス側（全体）
    0, 0, view_canvas.width, view_canvas.height  # 物理キャンバス側（全体）
)