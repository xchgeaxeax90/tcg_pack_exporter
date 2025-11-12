import os
import logging

from PIL import Image, ImageDraw

from nyan_tcg_game.cards import Card
logger = logging.getLogger(__name__)

border_color = (255, 189, 123)
border_outline_width = 3
border_width = 28
border_radius = 40

header_width = 566
header_ypos = 20
header_height = 60

company_xy = (13, 672)
company_bbox = (*company_xy, company_xy[0] + 350, company_xy[1] + 60)

rarity_xy = (426, 672)
rarity_width = 162
rarity_bbox = (*rarity_xy, rarity_xy[0] + rarity_width, rarity_xy[1] + 60)

textbox_radius = 20
textbox_border_width = 2
textbox_color = (213, 213, 213)

def inset_box(box, inset):
    x1, y1, x2, y2 = box
    return (x1 + inset, y1 + inset, x2 - inset, y2 - inset)


class CardFrame:
    def __init__(self, card, image_directory):
        self.card = card
        self.load_image(image_directory)
        # Do the actual preview generation
        self.create_preview_frame(600, 800)
        self.draw_header()
        self.draw_company()
        self.draw_rarity()


    def load_image(self, image_directory):
        """Loads the card's resized/cropped image into memory"""
        filename = os.path.join(image_directory, self.card.resized_uri)
        logger.debug(f'Opening image from {filename}')
        self.card_image = Image.open(filename)

    def create_preview_frame(self, dim_w, dim_h):
        """Creates the card preview image, loads the card's cropped image into the preview"""
        self.preview = Image.new(mode="RGBA", size=(dim_w, dim_h), color=(0,0,0,0))
        self.preview_draw = ImageDraw.Draw(self.preview)
        border_outer_bbox = inset_box((0, 0, dim_w-1, dim_h-1), 1)

        self.preview_draw.rounded_rectangle(border_outer_bbox,
                                            fill=border_color,
                                            radius=border_radius,
                                            width=border_outline_width,
                                            outline=(0, 0, 0))

        border_inner_bbox = inset_box(border_outer_bbox, 28)
        self.preview_draw.rounded_rectangle(border_inner_bbox,
                                            fill=border_color,
                                            radius=border_radius,
                                            width=border_outline_width,
                                            outline=(0, 0, 0))

        mask = Image.new(mode="RGBA", size=(dim_w, dim_h))
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle(inset_box(border_inner_bbox, border_outline_width),
                                    fill=(255, 255, 255, 255),
                                    radius=border_radius-border_outline_width-1)
        

        card_w, card_h = self.card_image.size
        offset = ((dim_w - card_w) // 2, (dim_h - card_h) // 2)
        overlay = Image.new(mode="RGBA", size=(dim_w, dim_h))
        overlay.paste(self.card_image, offset)
        self.preview.paste(overlay, mask=mask)

    def draw_textbox(self, bbox, text, font_size):
        self.preview_draw.rounded_rectangle(bbox,
                                            fill=textbox_color,
                                            radius=textbox_radius,
                                            width=textbox_border_width,
                                            outline=(0,0,0))
        bbox_center = ((bbox[0] + bbox[2]) // 2, (bbox[1] + bbox[3]) // 2)
        if text:
            self.preview_draw.text(bbox_center, text,
                                fill="white", anchor="mm",
                                stroke_fill="black",
                                stroke_width=2,
                                font_size=font_size)
        return bbox_center
        

    def draw_header(self):
        w, h = self.preview.size
        x1 = (w - header_width) // 2
        x2 = x1 + header_width
        header_bbox = (x1, header_ypos, x2, header_ypos + header_height)
        self.draw_textbox(header_bbox, self.card.card_name, 40)
                                            
    def draw_company(self):
        self.draw_textbox(company_bbox, self.card.company, 40)

    def draw_rarity(self):
        bbox_center = self.draw_textbox(rarity_bbox, None, 0)

        print_center = (bbox_center[0] - 30, bbox_center[1])

        self.preview_draw.text(print_center, "1",
                            fill=textbox_color, anchor="mm",
                            stroke_fill="black",
                            stroke_width=2,
                            font_size=35)

        rarity_center = (bbox_center[0] + 48, bbox_center[1])
        self.preview_draw.text(rarity_center, self.card.rarity.short_name,
                            fill="gold", anchor="mm",
                            stroke_fill="black",
                            stroke_width=2,
                            font_size=35)

        self.preview_draw.line((526, 680, 526, 722), fill="black", width=2)


    def create_frame(self, width):
        w, h = self.preview.size
        self.preview_draw.rounded_rectangle((0, 0, 100, 100), fill=0, radius=20)


    def save_preview(self, output_directory):
        filename = os.path.join(output_directory, self.card.get_image_filename('.png'))
        logger.debug(f'Writing image to {filename}')
        self.preview.save(filename)
        


def generate_previews(cards: list[Card], image_directory: str, output_directory: str):
    os.makedirs(output_directory, exist_ok=True)
    for card in cards:
        frame = CardFrame(card, image_directory)

        frame.save_preview(output_directory)


