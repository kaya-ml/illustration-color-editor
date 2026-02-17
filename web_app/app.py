import streamlit as st
import cv2
import numpy as np
from streamlit_image_coordinates import streamlit_image_coordinates

# 初期設定
st.set_page_config(page_title="イラスト 色置換・背景透過ツール", layout="wide")

# セッション状態の初期化
if "img_work" not in st.session_state:
    st.session_state.img_work = None
if "points" not in st.session_state:
    st.session_state.points = []
if "history" not in st.session_state:
    st.session_state.history = []
if "reset_trigger" not in st.session_state:
    st.session_state.reset_trigger = 0 

# Utility Functions
def hex_to_bgr(hex_color):
    hex_color = hex_color.lstrip("#")
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return (b, g, r)

def checkerboard(w, h, size=20):
    bg = np.zeros((h, w, 3), dtype=np.uint8)
    for y in range(0, h, size):
        for x in range(0, w, size):
            bg[y:y+size, x:x+size] = 200 if (x//size + y//size) % 2 == 0 else 255
    return bg

def preview_rgba(img_rgba):
    h, w = img_rgba.shape[:2]
    bg = checkerboard(w, h)
    alpha = (img_rgba[:, :, 3:4] / 255.0)
    rgb = img_rgba[:, :, :3]
    display_bgr = (rgb * alpha + bg * (1 - alpha)).astype(np.uint8)
    return cv2.cvtColor(display_bgr, cv2.COLOR_BGR2RGB)

# 画像処理
def floodfill_replace(img_rgba, x, y, new_bgr, tol):
    bgr = img_rgba[:, :, :3].copy()
    alpha = img_rgba[:, :, 3].copy()
    h, w = bgr.shape[:2]
    mask = np.zeros((h + 2, w + 2), np.uint8)
    cv2.floodFill(bgr, mask, (x, y), new_bgr, (tol,)*3, (tol,)*3, flags=cv2.FLOODFILL_FIXED_RANGE)
    return np.dstack((bgr, alpha))

def floodfill_transparent(img_rgba, x, y, tol):
    bgr = img_rgba[:, :, :3].copy()
    alpha = img_rgba[:, :, 3].copy()
    h, w = bgr.shape[:2]
    mask = np.zeros((h + 2, w + 2), np.uint8)
    cv2.floodFill(bgr.copy(), mask, (x, y), (0, 0, 0), (tol,)*3, (tol,)*3, flags=cv2.FLOODFILL_MASK_ONLY | cv2.FLOODFILL_FIXED_RANGE)
    fill = mask[1:-1, 1:-1]
    alpha[fill == 1] = 0
    return np.dstack((bgr, alpha))

# メインロジック
st.title("🎨 イラスト 色置換・背景透過ツール")

uploaded = st.file_uploader("画像をアップロード", type=["png", "jpg", "jpeg"])

if uploaded:
    file_id = f"{uploaded.name}_{uploaded.size}"
    if "current_file_id" not in st.session_state or st.session_state.current_file_id != file_id:
        data = np.frombuffer(uploaded.read(), np.uint8)
        img = cv2.imdecode(data, cv2.IMREAD_UNCHANGED)
        if img is not None:
            if img.shape[2] == 3:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
            st.session_state.img_work = img
            st.session_state.points = []
            st.session_state.history = []
            st.session_state.current_file_id = file_id
            st.session_state.reset_trigger += 1

if st.session_state.img_work is not None:
    # サイドバー設定
    st.sidebar.header("🔧 設定")
    mode = st.sidebar.radio("モード選択", ["クリック色置換", "クリック背景透過"])
    tol = st.sidebar.slider("許容範囲 (Tolerance)", 0, 100, 20)
    
    if mode == "クリック色置換":
        color_hex = st.sidebar.color_picker("置換後の色", "#FF0000")
        new_bgr = hex_to_bgr(color_hex)

    # プレビュー表示
    preview_img = preview_rgba(st.session_state.img_work)
    st.write("### プレビュー (クリックして地点を選択)")
    
    # 座標取得コンポーネント
    coords = streamlit_image_coordinates(
        preview_img, 
        key=f"coords_{st.session_state.reset_trigger}"
    )

    if coords:
        new_point = (coords["x"], coords["y"])
        # 同じ場所の連続クリックを無視しつつ追加
        if not st.session_state.points or st.session_state.points[-1] != new_point:
            st.session_state.points.append(new_point)
            st.rerun()

    # ステータス表示
    st.info(f"📍 選択中のポイント: {len(st.session_state.points)} 個")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("▶ 実行", type="primary", use_container_width=True):
            if st.session_state.points:
                st.session_state.history.append(st.session_state.img_work.copy())
                if len(st.session_state.history) > 10:
                    st.session_state.history.pop(0)
                
                current_img = st.session_state.img_work.copy()
                for px, py in st.session_state.points:
                    if mode == "クリック色置換":
                        current_img = floodfill_replace(current_img, px, py, new_bgr, tol)
                    else:
                        current_img = floodfill_transparent(current_img, px, py, tol)
                
                st.session_state.img_work = current_img
                st.session_state.points = [] 
                st.session_state.reset_trigger += 1
                st.rerun()

    with col2:
        if st.button("⏪ 画像を元に戻す", use_container_width=True, disabled=len(st.session_state.history) == 0):
            st.session_state.img_work = st.session_state.history.pop()
            st.session_state.points = []
            st.session_state.reset_trigger += 1
            st.rerun()

    with col3:
        if st.button("↩ 点を一つ消す", use_container_width=True, disabled=len(st.session_state.points) == 0):
            st.session_state.points.pop()
            st.session_state.reset_trigger += 1
            st.rerun()

    with col4:
        if st.button("🗑 全点リセット", use_container_width=True):
            st.session_state.points = []
            st.session_state.reset_trigger += 1
            st.rerun()

    # ダウンロードエリア
    st.divider()
    res_ok, buffer = cv2.imencode(".png", st.session_state.img_work)
    if res_ok:
        st.download_button(
            label="📥 編集済み画像をPNGで保存",
            data=buffer.tobytes(),
            file_name="processed_stamp.png",
            mime="image/png",
            use_container_width=True
        )