"""
桌面宠物程序 - Desktop Pet
使用用户提供的角色图片制作的 Windows 桌面宠物
"""

import tkinter as tk
from tkinter import Menu
from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageEnhance
import random
import math
import sys
import os


def get_resource_path(relative_path):
    """获取资源文件路径（兼容 PyInstaller 打包）"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)


class DesktopPet:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("桌面宠物")
        self.root.overrideredirect(True)  # 无边框
        self.root.wm_attributes("-topmost", True)  # 始终置顶
        self.root.config(bg='systemTransparent' if sys.platform == 'darwin' else 'black')
        self.root.wm_attributes("-transparentcolor", "black")  # 黑色透明

        # --- 状态变量 ---
        self.base_scale = 0.25  # 基础缩放比例
        self.scale = self.base_scale
        self.is_topmost = True
        self.drag_data = {"x": 0, "y": 0}
        self.click_start = {"x": 0, "y": 0}
        self.is_dragging = False
        self.current_animation = None
        self.anim_frame = 0
        self.anim_timer = None
        self.bubble_timer = None
        self.bubble_visible = False
        self.idle_timer = None
        self.bounce_phase = 0

        # --- 加载图片 ---
        img_path = get_resource_path("character_rgba.png")
        self.original_image = Image.open(img_path).convert("RGBA")
        self.update_character_image()

        # --- 创建画布 ---
        self.canvas = tk.Canvas(
            self.root,
            width=self.char_width,
            height=self.char_height + 80,  # 额外空间给气泡
            bg="black",
            highlightthickness=0,
            bd=0
        )
        self.canvas.pack()

        # 显示角色
        self.char_img_tk = ImageTk.PhotoImage(self.char_image)
        self.char_item = self.canvas.create_image(
            self.char_width // 2,
            self.char_height // 2,
            image=self.char_img_tk,
            anchor="center"
        )

        # 气泡文字（初始隐藏）
        self.bubble_text = self.canvas.create_text(
            self.char_width // 2,
            -100,  # 隐藏在画布外
            text="",
            font=("微软雅黑", 10, "bold"),
            fill="#333333",
            justify="center",
            width=150
        )
        self.bubble_bg = self.canvas.create_oval(0, 0, 0, 0, fill="white", outline="#dddddd", width=1)
        self.canvas.tag_raise(self.bubble_text)

        # --- 绑定事件 ---
        self.root.bind("<Button-1>", self.on_left_click)
        self.root.bind("<B1-Motion>", self.on_drag)
        self.root.bind("<ButtonRelease-1>", self.on_left_release)
        self.root.bind("<Button-3>", self.show_context_menu)
        self.root.bind("<MouseWheel>", self.on_mouse_wheel)

        # --- 右键菜单 ---
        self.create_context_menu()

        # --- 窗口位置 ---
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = screen_w - self.char_width - 50
        y = screen_h - self.char_height - 150
        self.root.geometry(f"+{x}+{y}")

        # --- 开始空闲动画 ---
        self.start_idle_animation()

    def update_character_image(self):
        """根据缩放比例更新角色图片"""
        w = int(self.original_image.width * self.scale)
        h = int(self.original_image.height * self.scale)
        self.char_image = self.original_image.resize((w, h), Image.LANCZOS)
        self.char_width = w
        self.char_height = h

    # ====== 对话气泡 ======

    BUBBLE_TEXTS = {
        "jump": [
            "哇~跳起来啦！",
            "我要飞得更高~",
            "蹦蹦跳跳真开心！",
            "诶嘿~✨",
        ],
        "squish": [
            "噗叽~被压扁了！",
            "呜呜我变平了...",
            "弹性十足！",
            "压扁弹回来~",
        ],
        "shake": [
            "不要摇我啦！",
            "晕了晕了~",
            "摇摇摇~嘿嘿",
            "停不下来了！",
        ],
        "eat": [
            "蛋糕好好吃！",
            "再来一块嘛~",
            "幸福的味道🍰",
            "吃货的快乐~",
        ],
        "cute": [
            "你看我可爱吗？",
            "(*^▽^*)",
            "眨眨眼~✨",
            "卖萌是我的技能！",
        ],
        "smile": [
            "今天也要开心哦~",
            "嘿嘿，你好呀！",
            "心情超好的！",
            "笑一个😊",
        ],
        "angry": [
            "哼！生气了！",
            "不理你了！(╯‵□′)╯",
            "我才没有生气！",
            "哼哼哼！",
        ],
        "cry": [
            "呜呜呜...T_T",
            "好伤心啊...",
            "眼泪停不下来...",
            "需要安慰...",
        ],
    }

    def show_bubble(self, anim_type):
        """显示对话气泡"""
        if self.bubble_timer:
            self.root.after_cancel(self.bubble_timer)

        text = random.choice(self.BUBBLE_TEXTS.get(anim_type, ["..."]))
        self.canvas.itemconfig(self.bubble_text, text=text)

        # 计算气泡位置（角色头顶上方）
        cx = self.char_width // 2
        bubble_y = max(20, int(self.char_height * 0.05))

        # 更新文字位置
        self.canvas.coords(self.bubble_text, cx, bubble_y)

        # 计算气泡背景大小
        self.canvas.update_idletasks()
        bbox = self.canvas.bbox(self.bubble_text)
        if bbox:
            pad = 12
            self.canvas.coords(self.bubble_bg,
                               bbox[0] - pad, bbox[1] - pad,
                               bbox[2] + pad, bbox[3] + pad)
            self.canvas.itemconfig(self.bubble_bg, state="normal")
            self.canvas.tag_raise(self.bubble_bg)
            self.canvas.tag_raise(self.bubble_text)

        self.bubble_visible = True
        self.bubble_timer = self.root.after(2500, self.hide_bubble)

    def hide_bubble(self):
        """隐藏气泡"""
        self.canvas.coords(self.bubble_text, -100, -100)
        self.canvas.itemconfig(self.bubble_bg, state="hidden")
        self.bubble_visible = False

    # ====== 动画系统 ======

    def start_idle_animation(self):
        """开始空闲呼吸/弹跳动画"""
        self.idle_bounce()

    def idle_bounce(self):
        """空闲时微微上下弹跳"""
        if self.current_animation:
            self.idle_timer = self.root.after(100, self.idle_bounce)
            return

        self.bounce_phase += 0.15
        offset_y = int(math.sin(self.bounce_phase) * 3)
        self.canvas.coords(self.char_item,
                           self.char_width // 2,
                           self.char_height // 2 + offset_y)
        self.idle_timer = self.root.after(50, self.idle_bounce)

    def run_animation(self, anim_type):
        """播放指定动画"""
        if self.current_animation:
            return
        self.current_animation = anim_type
        self.anim_frame = 0
        self.show_bubble(anim_type)

        anim_funcs = {
            "jump": self.anim_jump,
            "squish": self.anim_squish,
            "shake": self.anim_shake,
            "eat": self.anim_eat,
            "cute": self.anim_cute,
            "smile": self.anim_smile,
            "angry": self.anim_angry,
            "cry": self.anim_cry,
        }
        func = anim_funcs.get(anim_type, self.anim_jump)
        func()

    def anim_done(self):
        """动画结束"""
        self.current_animation = None
        self.anim_frame = 0
        # 恢复原始图片
        self.char_img_tk = ImageTk.PhotoImage(self.char_image)
        self.canvas.itemconfig(self.char_item, image=self.char_img_tk)
        self.canvas.coords(self.char_item, self.char_width // 2, self.char_height // 2)

    def anim_jump(self):
        """跳跃动画"""
        frames = 20
        if self.anim_frame >= frames:
            self.anim_done()
            return

        t = self.anim_frame / frames
        # 抛物线运动
        jump_height = 60
        offset_y = -int(jump_height * 4 * t * (1 - t))
        # 空中稍微拉伸
        stretch = 1.0 + 0.1 * math.sin(t * math.pi)

        w = int(self.char_width * (1 / stretch if t < 0.5 else stretch))
        h = int(self.char_height * stretch)
        stretched = self.char_image.resize((w, h), Image.LANCZOS)

        self.char_img_tk = ImageTk.PhotoImage(stretched)
        self.canvas.itemconfig(self.char_item, image=self.char_img_tk)
        self.canvas.coords(self.char_item, self.char_width // 2, self.char_height // 2 + offset_y)

        self.anim_frame += 1
        self.anim_timer = self.root.after(30, self.anim_jump)

    def anim_squish(self):
        """压扁回弹动画"""
        frames = 24
        if self.anim_frame >= frames:
            self.anim_done()
            return

        t = self.anim_frame / frames
        # 先压扁再弹回再恢复
        if t < 0.3:
            # 压扁
            squash = 1.0 - 0.4 * (t / 0.3)
            stretch_x = 1.0 + 0.3 * (t / 0.3)
        elif t < 0.6:
            # 弹回（拉高）
            local_t = (t - 0.3) / 0.3
            squash = 0.6 + 0.6 * local_t
            stretch_x = 1.3 - 0.3 * local_t
        else:
            # 恢复
            local_t = (t - 0.6) / 0.4
            squash = 1.2 - 0.2 * local_t
            stretch_x = 1.0 + 0.05 * math.sin(local_t * math.pi * 2)

        w = int(self.char_width * stretch_x)
        h = int(self.char_height * squash)
        img = self.char_image.resize((w, h), Image.LANCZOS)

        self.char_img_tk = ImageTk.PhotoImage(img)
        self.canvas.itemconfig(self.char_item, image=self.char_img_tk)
        self.canvas.coords(self.char_item, self.char_width // 2, self.char_height // 2 + (self.char_height - h) // 2)

        self.anim_frame += 1
        self.anim_timer = self.root.after(30, self.anim_squish)

    def anim_shake(self):
        """左右抖动动画"""
        frames = 30
        if self.anim_frame >= frames:
            self.anim_done()
            return

        t = self.anim_frame / frames
        amplitude = 15 * (1 - t)  # 逐渐衰减
        offset_x = int(amplitude * math.sin(t * math.pi * 8))

        self.canvas.coords(self.char_item,
                           self.char_width // 2 + offset_x,
                           self.char_height // 2)

        self.anim_frame += 1
        self.anim_timer = self.root.after(30, self.anim_shake)

    def anim_eat(self):
        """吃蛋糕动画 - 嘴巴开合 + 小幅上下"""
        frames = 30
        if self.anim_frame >= frames:
            self.anim_done()
            return

        t = self.anim_frame / frames
        # 咀嚼动作
        chew = math.sin(t * math.pi * 6) * 5
        # 轻微上下
        bounce = math.sin(t * math.pi * 3) * 3

        self.canvas.coords(self.char_item,
                           self.char_width // 2,
                           self.char_height // 2 + int(bounce + chew))

        # 每隔几帧切换轻微缩放模拟咀嚼
        scale_factor = 1.0 + 0.02 * math.sin(t * math.pi * 6)
        w = int(self.char_width * scale_factor)
        h = int(self.char_height * (2 - scale_factor))
        img = self.char_image.resize((w, h), Image.LANCZOS)
        self.char_img_tk = ImageTk.PhotoImage(img)
        self.canvas.itemconfig(self.char_item, image=self.char_img_tk)

        self.anim_frame += 1
        self.anim_timer = self.root.after(50, self.anim_eat)

    def anim_cute(self):
        """卖萌动画 - 左右摇摆 + 轻微缩放"""
        frames = 40
        if self.anim_frame >= frames:
            self.anim_done()
            return

        t = self.anim_frame / frames
        sway = math.sin(t * math.pi * 4) * 10
        scale_factor = 1.0 + 0.05 * math.sin(t * math.pi * 2)

        w = int(self.char_width * scale_factor)
        h = int(self.char_height * scale_factor)
        img = self.char_image.resize((w, h), Image.LANCZOS)

        self.char_img_tk = ImageTk.PhotoImage(img)
        self.canvas.itemconfig(self.char_item, image=self.char_img_tk)
        self.canvas.coords(self.char_item,
                           self.char_width // 2 + int(sway),
                           self.char_height // 2)

        self.anim_frame += 1
        self.anim_timer = self.root.after(40, self.anim_cute)

    def anim_smile(self):
        """微笑动画 - 轻微上下点头"""
        frames = 30
        if self.anim_frame >= frames:
            self.anim_done()
            return

        t = self.anim_frame / frames
        nod = math.sin(t * math.pi * 3) * 8

        self.canvas.coords(self.char_item,
                           self.char_width // 2,
                           self.char_height // 2 + int(nod))

        self.anim_frame += 1
        self.anim_timer = self.root.after(40, self.anim_smile)

    def anim_angry(self):
        """生气动画 - 剧烈抖动 + 变红"""
        frames = 35
        if self.anim_frame >= frames:
            self.anim_done()
            return

        t = self.anim_frame / frames
        intensity = 12 * (1 - t * 0.5)
        offset_x = int(intensity * (random.random() - 0.5) * 2)
        offset_y = int(intensity * (random.random() - 0.5) * 2)

        # 稍微变红
        img = self.char_image.copy()
        red_overlay = Image.new("RGBA", img.size, (255, 100, 100, int(40 * (1 - t))))
        img = Image.alpha_composite(img, red_overlay)

        self.char_img_tk = ImageTk.PhotoImage(img)
        self.canvas.itemconfig(self.char_item, image=self.char_img_tk)
        self.canvas.coords(self.char_item,
                           self.char_width // 2 + offset_x,
                           self.char_height // 2 + offset_y)

        self.anim_frame += 1
        self.anim_timer = self.root.after(30, self.anim_angry)

    def anim_cry(self):
        """哭泣动画 - 缓慢上下 + 轻微缩小"""
        frames = 40
        if self.anim_frame >= frames:
            self.anim_done()
            return

        t = self.anim_frame / frames
        # 抽泣动作
        sob = abs(math.sin(t * math.pi * 5)) * 5
        # 轻微缩小
        shrink = 1.0 - 0.05 * math.sin(t * math.pi)

        w = int(self.char_width * shrink)
        h = int(self.char_height * shrink)
        img = self.char_image.resize((w, h), Image.LANCZOS)

        self.char_img_tk = ImageTk.PhotoImage(img)
        self.canvas.itemconfig(self.char_item, image=self.char_img_tk)
        self.canvas.coords(self.char_item,
                           self.char_width // 2,
                           self.char_height // 2 + int(sob))

        self.anim_frame += 1
        self.anim_timer = self.root.after(40, self.anim_cry)

    # ====== 事件处理 ======

    def on_left_click(self, event):
        """鼠标左键按下"""
        self.drag_data["x"] = event.x_root
        self.drag_data["y"] = event.y_root
        self.click_start["x"] = event.x_root
        self.click_start["y"] = event.y_root
        self.is_dragging = False

    def on_drag(self, event):
        """鼠标拖动"""
        dx = event.x_root - self.drag_data["x"]
        dy = event.y_root - self.drag_data["y"]

        # 判断是否开始拖动（移动超过5像素）
        if not self.is_dragging:
            total_dx = abs(event.x_root - self.click_start["x"])
            total_dy = abs(event.y_root - self.click_start["y"])
            if total_dx > 5 or total_dy > 5:
                self.is_dragging = True

        if self.is_dragging:
            x = self.root.winfo_x() + dx
            y = self.root.winfo_y() + dy
            self.root.geometry(f"+{x}+{y}")

        self.drag_data["x"] = event.x_root
        self.drag_data["y"] = event.y_root

    def on_left_release(self, event):
        """鼠标左键释放 - 如果不是拖动，则触发互动"""
        if not self.is_dragging:
            # 点击触发随机动画
            anims = ["jump", "squish", "shake", "eat", "cute", "smile", "angry", "cry"]
            self.run_animation(random.choice(anims))
        self.is_dragging = False

    def on_mouse_wheel(self, event):
        """鼠标滚轮调整大小"""
        delta = event.delta
        if delta > 0:
            self.base_scale = min(0.8, self.base_scale + 0.02)
        else:
            self.base_scale = max(0.1, self.base_scale - 0.02)

        self.scale = self.base_scale
        self.update_character_image()

        # 更新窗口大小
        self.canvas.config(width=self.char_width, height=self.char_height + 80)
        self.char_img_tk = ImageTk.PhotoImage(self.char_image)
        self.canvas.itemconfig(self.char_item, image=self.char_img_tk)
        self.canvas.coords(self.char_item, self.char_width // 2, self.char_height // 2)

        # 重新定位窗口保持底部对齐
        new_h = self.char_height + 80
        current_y = self.root.winfo_y()
        current_h = self.root.winfo_height()
        new_y = current_y + current_h - new_h
        self.root.geometry(f"{self.char_width}x{new_h}+{self.root.winfo_x()}+{new_y}")

    # ====== 右键菜单 ======

    def create_context_menu(self):
        """创建右键菜单"""
        self.context_menu = Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="🔄 调整大小", command=self.show_size_menu)
        self.context_menu.add_command(label="📌 取消置顶" if self.is_topmost else "📌 置顶",
                                      command=self.toggle_topmost)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="❌ 退出", command=self.root.quit)

        self.size_menu = Menu(self.context_menu, tearoff=0)
        sizes = [("小巧 (15%)", 0.15), ("小 (20%)", 0.20), ("标准 (25%)", 0.25),
                 ("中 (35%)", 0.35), ("大 (45%)", 0.45), ("超大 (60%)", 0.60)]
        for label, s in sizes:
            self.size_menu.add_command(label=label, command=lambda sc=s: self.set_size(sc))

    def show_context_menu(self, event):
        """显示右键菜单"""
        # 更新菜单文字
        self.context_menu.entryconfig(1, label="📌 取消置顶" if self.is_topmost else "📌 置顶")
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def show_size_menu(self):
        """显示子菜单"""
        try:
            self.size_menu.tk_popup(self.root.winfo_x() + 50, self.root.winfo_y() + 50)
        finally:
            self.size_menu.grab_release()

    def toggle_topmost(self):
        """切换置顶状态"""
        self.is_topmost = not self.is_topmost
        self.root.wm_attributes("-topmost", self.is_topmost)

    def set_size(self, scale):
        """设置角色大小"""
        self.base_scale = scale
        self.scale = scale
        self.update_character_image()
        self.canvas.config(width=self.char_width, height=self.char_height + 80)
        self.char_img_tk = ImageTk.PhotoImage(self.char_image)
        self.canvas.itemconfig(self.char_item, image=self.char_img_tk)
        self.canvas.coords(self.char_item, self.char_width // 2, self.char_height // 2)
        # 保持底部对齐
        new_h = self.char_height + 80
        current_y = self.root.winfo_y()
        current_h = self.root.winfo_height()
        new_y = current_y + current_h - new_h
        self.root.geometry(f"{self.char_width}x{new_h}+{self.root.winfo_x()}+{new_y}")

    def run(self):
        """运行程序"""
        self.root.mainloop()


if __name__ == "__main__":
    pet = DesktopPet()
    pet.run()
