import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os

# ===== CONFIG =====
ASPECT_RATIO = (16, 9)  # (width, height)
OUTPUT_SIZE = (550, 750)  # target size after crop/resize
OUTPUT_DIR = "cropped_output"

class CropTool:
    def __init__(self, root, cards, output_directory):
        self.root = root
        self.cards = cards
        self.output_directory = output_directory
        self.current_index = 0
        self.start_x = self.start_y = None
        self.rect = None
        self.crop_coords = None
        self.scale = 1.0

        os.makedirs(self.output_directory, exist_ok=True)

        # --- UI ---
        self.canvas = tk.Canvas(root, cursor="cross")
        self.canvas.pack(fill="both", expand=True)

        btn_frame = tk.Frame(root)
        btn_frame.pack(fill="x", pady=5)
        tk.Button(btn_frame, text="Crop & Next", command=self.crop_and_next).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Skip", command=self.next_image).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Quit", command=root.quit).pack(side="right", padx=5)

        # --- Image handling ---
        self.root.bind("<Configure>", self.on_resize)
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        self.img = None
        self.tk_img = None
        self.display_img = None
        self.load_image()

    def load_image(self):
        if self.current_index >= len(self.cards):
            messagebox.showinfo("Done", "All images processed!")
            self.root.quit()
            return

        path = self.cards[self.current_index].source_uri
        self.img = Image.open(path)
        self.root.title(f"Cropping ({self.current_index+1}/{len(self.cards)}): {os.path.basename(path)}")
        self.display_image()

    def display_image(self):
        if not self.img:
            return

        self.canvas.delete("all")
        cw = max(self.canvas.winfo_width(), 800)
        ch = max(self.canvas.winfo_height(), 600)

        iw, ih = self.img.size
        scale = min(cw/iw, ch/ih)
        self.scale = scale
        new_w, new_h = int(iw*scale), int(ih * scale)
        self.display_img = self.img.resize((new_w, new_h), Image.LANCZOS)
        self.tk_img = ImageTk.PhotoImage(self.display_img)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)
        self.canvas.image = self.tk_img

    def on_resize(self, event):
        self.display_image()

    def on_press(self, event):
        self.start_x, self.start_y = event.x, event.y
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red", width=2)

    def on_drag(self, event):
        if not self.start_x or not self.start_y:
            return

        # Maintain aspect ratio
        dx = event.x - self.start_x
        dy = event.y - self.start_y
        target_ratio = OUTPUT_SIZE[0] / OUTPUT_SIZE[1]

        if abs(dx) > abs(dy):
            width = dx
            height = int(dx / target_ratio)
        else:
            height = dy
            width = int(dy * target_ratio)

        x1 = self.start_x
        y1 = self.start_y
        x2 = x1 + width
        y2 = y1 + height

        self.canvas.coords(self.rect, x1, y1, x2, y2)

    def on_release(self, event):
        if self.rect:
            self.crop_coords = self.canvas.coords(self.rect)

    def crop_and_next(self):
        if not self.crop_coords:
            messagebox.showwarning("No selection", "Please draw a crop rectangle first.")
            return

        x1, y1, x2, y2 = [int(c / self.scale) for c in self.crop_coords]
        cropped = self.img.crop((x1, y1, x2, y2)).resize(OUTPUT_SIZE, Image.LANCZOS)

        filename = self.cards[self.current_index].resized_uri
        save_path = os.path.join(self.output_directory, filename)
        cropped.save(save_path)
        print(f"Saved: {save_path}")

        self.next_image()

    def next_image(self):
        self.current_index += 1
        self.crop_coords = None
        self.load_image()

def run_gui(cards, output_directory):
    if not cards:
        return
    root = tk.Tk()
    app = CropTool(root, cards, output_directory)
    root.mainloop()

def crop_images(cards, output_directory):
    resize_needed = []
    for card in cards:
        filename = os.path.join(output_directory, card.get_image_filename('.png'))
        card.resized_uri = card.get_image_filename('.png')
        if not os.path.exists(filename):
            resize_needed.append(card)
    run_gui(resize_needed, output_directory)
    return cards
