import cv2
import numpy as np
import os
from tkinter import Tk, Button, Label, filedialog, colorchooser, messagebox, Canvas, Scale, HORIZONTAL
from PIL import Image, ImageTk

class ColorReplaceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("色置換・透過ツール - LINEスタンプ対応")
        self.root.geometry("1000x750") 
        self.root.resizable(False, False)

        # 状態変数
        self.img = None
        self.img_rgb = None
        self.alpha = None
        self.display_img = None
        self.tk_img = None
        self.new_color = (0, 0, 0)
        self.base_color = None
        self.exclusion_color = None
        self.tolerance = 20
        self.is_picking_color = False
        self.is_picking_exclusion = False
        self.is_transparent_mode = False

        # ウィジェット配置
        self.setup_ui()

    def setup_ui(self):
        Label(self.root, text="色置換・背景透過ツール", font=("Meiryo", 18, "bold")).pack(pady=10)

        # 設定エリア
        setting_frame = Label(self.root)
        setting_frame.pack(pady=5)
        
        # 許容範囲
        self.tolerance_label = Label(setting_frame, text=f"許容範囲 (Tolerance): {self.tolerance}", font=("Meiryo", 10))
        self.tolerance_label.pack(side="left", padx=5)
        self.tolerance_scale = Scale(setting_frame, from_=1, to=100, orient=HORIZONTAL, length=150, 
                                     command=self.update_tolerance, showvalue=0)
        self.tolerance_scale.set(self.tolerance)
        self.tolerance_scale.pack(side="left", padx=5)
        
        # 色選択ボタン
        Button(setting_frame, text="使用する色を選択", command=self.choose_color, width=20, bg="#E0FFE0").pack(side="left", padx=5)
        
        # 置換後の色抽出ボタン
        self.pick_color_button = Button(setting_frame, text="使用する色を抽出", command=self.toggle_color_picker, width=25, bg="#FFFFE0")
        self.pick_color_button.pack(side="left", padx=5)
        
        # 除外色抽出ボタン
        self.exclude_color_button = Button(setting_frame, text="除外する色を選択", command=self.toggle_exclusion_picker, width=25, bg="#F0F0FF")
        self.exclude_color_button.pack(side="left", padx=5)

        # 操作エリア
        main_button_frame = Label(self.root)
        main_button_frame.pack(pady=10)

        Button(main_button_frame, text="画像を開く", command=self.load_image, width=25).pack(side="left", padx=5)
        Button(main_button_frame, text="置換結果を保存", command=self.save_image, width=25, bg="#F0F0FF").pack(side="left", padx=5)
        
        # 透過モードボタン
        self.transparent_button = Button(main_button_frame, text="【OFF】背景透過モード", command=self.toggle_transparent_mode, width=25, bg="#E8F8F5")
        self.transparent_button.pack(side="left", padx=5)
        
        # 一括処理ボタン
        batch_frame = Label(self.root)
        batch_frame.pack(pady=10)
        Label(batch_frame, text="--- 複数ファイル一括処理 ---", font=("Meiryo", 12)).pack()
        Button(batch_frame, text="一括置換実行 (フォルダ指定)", command=self.run_batch_replace, width=30, bg="#FFF0F0").pack(pady=5)

        # 画像を表示
        self.canvas = Canvas(self.root, width=512, height=512, bg="#CCCCCC", bd=2, relief="sunken") # 背景をグレーにして透過を確認しやすく
        self.canvas.pack(pady=10)

        # クリックイベント
        self.canvas.bind("<Button-1>", self.on_click)

    # 許容範囲の更新
    def update_tolerance(self, val):
        self.tolerance = int(val)
        self.tolerance_label.config(text=f"許容範囲 (Tolerance): {self.tolerance}")
    
    # 各モード切り替え
    def toggle_color_picker(self):
        self.is_picking_color = not self.is_picking_color
        if self.is_picking_color:
            self.pick_color_button.config(text="【ON】置換後の色を抽出中", bg="#FFD0D0")
            self.is_picking_exclusion = False; self.exclude_color_button.config(text="除外する色を抽出 (頬など)", bg="#F0F0FF")
            self.is_transparent_mode = False; self.transparent_button.config(text="【OFF】背景透過モード", bg="#E8F8F5")
    def toggle_exclusion_picker(self):
        self.is_picking_exclusion = not self.is_picking_exclusion
        if self.is_picking_exclusion:
            self.exclude_color_button.config(text="【ON】除外色を抽出中", bg="#C0E0FF")
            self.is_picking_color = False; self.pick_color_button.config(text="置換後の色を抽出 (クリック)", bg="#FFFFE0")
            self.is_transparent_mode = False; self.transparent_button.config(text="【OFF】背景透過モード", bg="#E8F8F5")
    
    # 透過モード切り替え
    def toggle_transparent_mode(self):
        self.is_transparent_mode = not self.is_transparent_mode
        if self.is_transparent_mode:
            self.transparent_button.config(text="【ON】背景透過モード (クリック)", bg="#A2D9CE")
            self.is_picking_color = False; self.pick_color_button.config(text="置換後の色を抽出 (クリック)", bg="#FFFFE0")
            self.is_picking_exclusion = False; self.exclude_color_button.config(text="除外する色を抽出 (頬など)", bg="#F0F0FF")
            messagebox.showinfo("モード変更", "背景透過モードになりました。\n画像をクリックすると、その部分が透明になります。")
        else:
            self.transparent_button.config(text="【OFF】背景透過モード", bg="#E8F8F5")

    # 画像読み込み
    def load_image(self):
        path = filedialog.askopenfilename(title="画像を選択してください", filetypes=[("PNG/JPEG画像", "*.png;*.jpg;*.jpeg")])
        if not path: return

        # 日本語対応
        try:
            with open(path, 'rb') as f: img_data = f.read()
            nparr = np.frombuffer(img_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
            if img is None: raise Exception("画像のデコードに失敗")
        except Exception as e:
            messagebox.showerror("エラー", f"画像の読み込みに失敗しました: {e}")
            return
             
        # 分離処理
        if img.shape[2] == 4:
            self.alpha = img[:, :, 3].copy()
            self.img_rgb = img[:, :, :3].copy()
        else:
            # 3ch画像の場合、不透明なアルファチャンネルを強制的に作成
            self.alpha = np.full(img.shape[:2], 255, dtype=np.uint8)
            self.img_rgb = img.copy()
            messagebox.showwarning("警告", "読み込んだ画像には透過情報がありませんでした。\n透過処理は可能ですが、保存後に透過が反映されているか確認してください。")

        self.display_img = self.img_rgb.copy()
        self.show_image(self.display_img)
        self.base_color = None 
        self.exclusion_color = None
        messagebox.showinfo("読み込み完了", "画像を読み込みました。")

    # 画像を表示
    def show_image(self, img):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        
        # アルファチャンネルをPIL画像に適用
        if self.alpha is not None:
            alpha_pil = Image.fromarray(self.alpha, 'L')
            img_pil.putalpha(alpha_pil)
        
        # リサイズ処理
        h, w = img.shape[:2]
        if w > 512 or h > 512:
            scale_factor = min(512 / w, 512 / h)
            new_w = int(w * scale_factor)
            new_h = int(h * scale_factor)
            img_pil = img_pil.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        self.tk_img = ImageTk.PhotoImage(img_pil)
        
        x_center = (512 - img_pil.width) // 2
        y_center = (512 - img_pil.height) // 2
        
        self.canvas.delete("all")
        self.canvas.create_image(x_center, y_center, anchor="nw", image=self.tk_img)

    # 新しい色を選択 (カラーピッカー)
    def choose_color(self):
        _, hex_color = colorchooser.askcolor(title="置換後の色を選択")
        if hex_color:
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)
            self.new_color = (b, g, r)
            messagebox.showinfo("選択完了", f"選んだ色: {hex_color} に設定されました。")

    # クリックイベント
    def on_click(self, event):
        if self.img_rgb is None: return messagebox.showwarning("警告", "まず画像を開いてください。")

        # 座標計算
        canvas_w, canvas_h = 512, 512
        img_h, img_w = self.img_rgb.shape[:2]
        if self.tk_img is None: return
        disp_w, disp_h = self.tk_img.width(), self.tk_img.height()
        x_offset = (canvas_w - disp_w) // 2; y_offset = (canvas_h - disp_h) // 2
        if not (x_offset <= event.x < x_offset + disp_w and y_offset <= event.y < y_offset + disp_h): return
        x = int((event.x - x_offset) / disp_w * img_w)
        y = int((event.y - y_offset) / disp_h * img_h)
        clicked_bgr = self.img_rgb[y, x].tolist()
        
        # モード分岐
        if self.is_transparent_mode:
            self.apply_transparent_fill(x, y)
        elif self.is_picking_exclusion:
            self.exclusion_color = tuple(clicked_bgr)
            hex_color = '#%02x%02x%02x' % (clicked_bgr[2], clicked_bgr[1], clicked_bgr[0])
            messagebox.showinfo("除外色抽出完了", f"除外色: {hex_color} を設定しました。")
            self.toggle_exclusion_picker() 
        elif self.is_picking_color:
            self.new_color = tuple(clicked_bgr)
            hex_color = '#%02x%02x%02x' % (clicked_bgr[2], clicked_bgr[1], clicked_bgr[0])
            messagebox.showinfo("色抽出完了", f"抽出した色: {hex_color} に置換後の色が設定されました。")
            self.toggle_color_picker()
        else:
            if self.new_color == (0, 0, 0) and self.base_color is None: return messagebox.showwarning("警告", "置換後の色を選択してください。")
            self.base_color = clicked_bgr
            self.apply_color_replace(self.base_color, x, y)


    # 背景透過処理
    def apply_transparent_fill(self, x, y):
        if self.alpha is None or self.img_rgb is None: return 
        
        h, w = self.img_rgb.shape[:2]
        mask = np.zeros((h + 2, w + 2), np.uint8)
        
        # 透明にしたい領域を取得
        retval, _, mask, _ = cv2.floodFill(
            self.img_rgb.copy(), mask, (x, y), (0, 0, 0),
            (self.tolerance,) * 3, (self.tolerance,) * 3,
            flags=cv2.FLOODFILL_MASK_ONLY | cv2.FLOODFILL_FIXED_RANGE
        )
        
        # 取得したマスクをアルファチャンネルに適用
        fill_mask = mask[1:-1, 1:-1]
        self.alpha[fill_mask == 1] = 0
        
        messagebox.showinfo("透過完了", f"FloodFillで選択された {retval} ピクセルを透明にしました。")
        
        # 透過結果を反映
        self.display_img = self.img_rgb.copy()
        self.show_image(self.display_img)
        
    # クリックで色置換 (FloodFill) 処理
    def apply_color_replace(self, base_color, x, y):
        if self.img_rgb is None or self.new_color is None: return
        
        h, w = self.img_rgb.shape[:2]
        mask = np.zeros((h + 2, w + 2), np.uint8)
        
        retval, _, mask, _ = cv2.floodFill(
            self.img_rgb.copy(), mask, (x, y), (0, 0, 0),
            (self.tolerance,) * 3, (self.tolerance,) * 3,
            flags=cv2.FLOODFILL_MASK_ONLY | cv2.FLOODFILL_FIXED_RANGE
        )
        
        fill_mask = mask[1:-1, 1:-1]
        self.img_rgb[fill_mask == 1] = self.new_color
        messagebox.showinfo("置換完了", f"{retval} ピクセルを置換しました。")
        
        self.display_img = self.img_rgb.copy()
        self.show_image(self.display_img)

    # 画像の保存
    def save_image(self):
        if self.img_rgb is None: return messagebox.showwarning("警告", "画像を開いてください。")

        # 初期ディレクトリをデスクトップに設定
        initial_dir = os.path.join(os.path.expanduser('~'), 'Desktop')
        if not os.path.exists(initial_dir): initial_dir = os.path.expanduser('~')
        
        save_path = filedialog.asksaveasfilename(
            title="置換結果を保存", initialdir=initial_dir, defaultextension=".png", filetypes=[("PNGファイル", "*.png")]
        )
        if save_path:
            try:
                # BGR画像とアルファチャンネルを再結合
                if self.alpha is not None:
                    result = np.dstack((self.img_rgb, self.alpha))
                else:
                    result = self.img_rgb
                    
                cv2.imwrite(save_path, result)
                messagebox.showinfo("保存完了", f"保存しました:\n{save_path}")
            except Exception as e:
                messagebox.showerror("保存エラー", f"ファイルの保存に失敗しました: {e}")

    # 一括置換実行
    def run_batch_replace(self):
        if self.new_color is None or self.new_color == (0, 0, 0): return messagebox.showwarning("警告", "置換後の色が設定されていません。")
        if self.base_color is None: return messagebox.showwarning("警告", "置換したい元の部分をクリックして基準色を設定してください。")
        
        folder_path = filedialog.askdirectory(title="スタンプ画像フォルダを選択してください")
        if not folder_path: return

        try:
            self.batch_replace_color(folder_path, self.base_color, self.new_color, self.tolerance)
            messagebox.showinfo("一括置換完了", f"フォルダ内の画像を処理し、新しいファイル名で保存しました。")
        except Exception as e:
            messagebox.showerror("エラー", f"一括置換中にエラーが発生しました: {e}")


    def batch_replace_color(self, target_dir, base_bgr_color, new_bgr_color, tolerance):
        # 許容範囲に基づいた BGR の下限と上限を計算
        tolerance_array = np.array([tolerance] * 3)
        lower_bound = np.clip(np.array(base_bgr_color) - tolerance_array, 0, 255)
        upper_bound = np.clip(np.array(base_bgr_color) + tolerance_array, 0, 255)

        processed_count = 0
        for filename in os.listdir(target_dir):
            if filename.endswith((".png", ".jpg", ".jpeg")):
                path = os.path.join(target_dir, filename)
                
                # 日本語対応
                try:
                    with open(path, 'rb') as f: img_data = f.read()
                    nparr = np.frombuffer(img_data, np.uint8)
                    img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
                except Exception: continue
                if img is None: continue

                # アルファチャンネル分離/作成
                if img.shape[2] == 4: bgr = img[:, :, :3].copy(); alpha = img[:, :, 3].copy()
                else: bgr = img.copy(); alpha = None

                # 置換したい色のマスク
                base_mask = cv2.inRange(bgr, lower_bound, upper_bound)
                final_mask = base_mask

                # 除外色マスクの適用
                if self.exclusion_color is not None:
                    ex_lower = np.clip(np.array(self.exclusion_color) - tolerance_array, 0, 255)
                    ex_upper = np.clip(np.array(self.exclusion_color) + tolerance_array, 0, 255)
                    exclusion_mask = cv2.inRange(bgr, ex_lower, ex_upper)
                    not_exclusion_mask = cv2.bitwise_not(exclusion_mask)
                    final_mask = cv2.bitwise_and(base_mask, not_exclusion_mask)

                # 最終マスクに基づいて色を置換
                bgr[final_mask > 0] = new_bgr_color

                # 画像を再結合して保存
                if alpha is not None: result = np.dstack((bgr, alpha))
                else: result = bgr
                base, ext = os.path.splitext(filename)
                save_path = os.path.join(target_dir, f"{base}_fixed{ext}")
                cv2.imwrite(save_path, result)
                processed_count += 1
        
        if processed_count == 0: messagebox.showwarning("警告", "指定されたフォルダ内に処理対象の画像ファイルが見つかりませんでした。")

# 実行
if __name__ == "__main__":
    root = Tk()
    app = ColorReplaceApp(root)
    root.mainloop()