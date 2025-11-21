import tkinter as tk
import logging
from tkinter import filedialog, messagebox, colorchooser
from PIL import Image, ImageTk, ImageColor
import os

logger = logging.getLogger(__name__)

# The images fed into nyan's tcg bot are required to be exactly
# 550x750 pixels However, the actual viewable area is slightly
# less. The card frame cuts off 8 pixels on each side of the image,
# leaving an area of 534x734. Finally, the card's nameplate cuts off
# an additional 46 pixels from the top of the image, yielding a final
# viewable area of 534x688 pixels

# This script allows the user to easily crop the image to the correct
# dimensions. The user is presented with a rectangle indicating the
# viewable area on the image that they would like to crop. When the
# crop button is selected, the GUI crops the image to the correct
# dimensions to be imported into the tcg bot, while the viewable area
# is positioned in the correct area on the card


OUTPUT_SIZE = (550, 750)  # target size after crop/resize
VISIBLE_SIZE = (534, 688)
VISIBLE_RECT_OFFSETS = (-8, -54, 8, 8)
OUTPUT_DIR = "cropped_output"

class CropTool:
    def __init__(self, root, cards, output_directory):
        self.root = root
        self.cards = cards
        self.output_directory = output_directory
        self.current_index = 0
        self.start_x = self.start_y = None
        self.rect = None
        self.crop_rect = None
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
        self.color_input = tk.Text(btn_frame, height=1, width=10)
        self.color_input.pack(side="right", padx=5)
        self.color_input.bind("<<Modified>>", self.on_color_update)
        tk.Button(btn_frame, text="Pick Color", command=self.pick_color).pack(side="right", padx=5)

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
        card = self.cards[self.current_index]
        logger.debug(f"Loading {card=}")

        path = card.local_image_path
        top_img = Image.open(path).convert("RGBA")
        bottom_img = Image.new(mode="RGBA", size=top_img.size, color=card.background_fill)
        self.img = Image.alpha_composite(bottom_img, top_img)
        #self.img.paste(top_img, (0, 0), top_img)

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

        offsetx, offsety = ((cw - new_w) // 2, 0)

        self.display_img = self.img.resize((new_w, new_h), Image.LANCZOS)
        self.tk_img = ImageTk.PhotoImage(self.display_img)
        self.canvas.create_image(offsetx, offsety, anchor="nw", image=self.tk_img)
        self.canvas.image = self.tk_img

        self.coord_offset = (offsetx, offsety)

    def on_color_update(self, event):
        text_widget = event.widget
        if text_widget.edit_modified():
            color_str = text_widget.get("1.0", "end-1c")
            try:
                color = ImageColor.getrgb(color_str)
                logger.debug(f"Setting color to {color}")
                self.cards[self.current_index].background_fill = color
                self.load_image()
            except:
                pass

            text_widget.edit_modified(False)   # MUST reset the flag!


    def on_resize(self, event):
        self.display_image()

    def on_press(self, event):
        self.start_x, self.start_y = event.x, event.y
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="blue", width=2)
        if self.crop_rect:
            self.canvas.delete(self.crop_rect)
        self.crop_rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red", width=2)

    def on_drag(self, event):
        if not self.start_x or not self.start_y:
            return

        # Maintain aspect ratio
        dx = event.x - self.start_x
        dy = event.y - self.start_y
        target_ratio = VISIBLE_SIZE[0] / VISIBLE_SIZE[1]

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
        crop_coords = self.get_crop_bbox_from_view_bbox((x1, y1, x2, y2))
        logger.debug(f"Crop rect coords: {crop_coords}")
        self.canvas.coords(self.crop_rect, *crop_coords)


    def on_release(self, event):
        if self.rect:
            x1, y1, x2, y2 = self.canvas.coords(self.crop_rect)
            ow, oh = self.coord_offset
            self.crop_coords = (x1 - ow, y1 - oh, x2 - ow, y2 - oh)

    def crop_and_next(self):
        if not self.crop_coords:
            messagebox.showwarning("No selection", "Please draw a crop rectangle first.")
            return

        x1, y1, x2, y2 = coords = [int(c / self.scale) for c in self.crop_coords]

        cropped = self.img.crop((x1, y1, x2, y2)).resize(OUTPUT_SIZE, Image.LANCZOS)

        filename = self.cards[self.current_index].get_image_filename('.png')
        save_path = os.path.join(self.output_directory, filename)
        logger.debug(f'{save_path=} {filename=}')
        cropped.save(save_path)
        print(f"Saved: {save_path}")

        self.next_image()

    def next_image(self):
        self.current_index += 1
        self.crop_coords = None
        self.load_image()

    def pick_color(self):
        color_str = self.color_input.get("1.0", "end-1c")
        logger.debug("Creating choose color dialog")
        ret = colorchooser.askcolor(color=color_str)
        self.color_input.replace("1.0", "end-1c", ret[1])

    def get_crop_bbox_from_view_bbox(self, view_bbox):
        x1, y1, x2, y2 = view_bbox
        w = x2-x1
        scale = w / VISIBLE_SIZE[0]
        return tuple(map(lambda x, y: x + y*scale, view_bbox, VISIBLE_RECT_OFFSETS))
        
    

def run_gui(cards, output_directory):
    if not cards:
        return
    root = tk.Tk()
    app = CropTool(root, cards, output_directory)
    root.mainloop()

def crop_images(cards, output_directory, export_prefix):
    logger.debug(output_directory)
    resize_needed = []
    for card in cards:
        filename = os.path.join(output_directory, card.get_image_filename('.png'))
        card.resized_uri = os.path.relpath(filename, export_prefix)
        if not os.path.exists(filename):
            resize_needed.append(card)
    run_gui(resize_needed, output_directory)
    return cards
