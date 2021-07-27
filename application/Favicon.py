from PIL import Image, ImageDraw, ImageFont

from application.paths import FONT_ARIAL_PATH


class Favicon:
    # Reference: https://next.material-ui.com/components/avatars/
    @staticmethod
    def text_to_color(text):
        text_hash = 0

        for char in text:
            text_hash = ord(char) + (text_hash << 5) - text_hash

        color_list = ['#']

        for i in range(3):
            value = (text_hash >> (i * 8)) & 0xff
            color_list.append(f'00{format(value, "x")}'[-2:])

        return ''.join(color_list)

    def __init__(self, text):
        if text.startswith('192'):
            self.short_text = text[-5:]
        else:
            self.short_text = text[:5]

        self.color = self.text_to_color(text)
        self.im = Image.new('RGBA', (228, 228))
        self.draw = ImageDraw.Draw(self.im)

        self.draw.ellipse((28, 28, 200, 200), fill=self.color)
        font = ImageFont.truetype(FONT_ARIAL_PATH, 60)
        w, h = self.draw.textsize(self.short_text, font=font)
        self.draw.text(((228 - w) / 2, (228 - h) / 2), self.short_text, font=font)

    def VNC(self, temp):
        self.draw.rectangle([(228 - 96, 228 - 96), (228, 228)], fill='#f08080')
        self.im.save(temp, format='png')

    def console(self, temp):
        self.draw.rectangle([(228 - 96, 228 - 96), (228, 228)], fill='black')
        self.im.save(temp, format='png')

    def file_manager(self, temp):
        self.draw.rectangle([(228 - 96, 228 - 96), (228, 228)], fill='#1976d2')
        self.im.save(temp, format='png')
