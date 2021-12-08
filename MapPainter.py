from PIL import ImageDraw, ImageFont, Image
from Entity import Boss

from Events import Blacksmith, Shop
from Gen import ChestGen

class MapPainter:
    def __init__(self, positions=None, Map=None):
        self.colors = [
            (155, 89, 182),
            (200, 155, 0),
            (144, 12, 63),
            (20, 82, 42),
            (33, 19, 165)
        ]
        self.font = ImageFont.truetype("img\\draw\\jf-openhuninn-1.1.ttf", 18, encoding='utf-8')
        
        if positions != None:
            self.draw_base(positions)
        elif Map != None:
            self.draw_base_from_map(Map)
        else:
            raise ValueError('either positions or map cannot be None')

    def draw_base_from_map(self, Map):
        positions = {"Shop": [], "Blacksmith": [], "ChestGen": [], "Boss": []}
        for i in range(len(Map)):
            if isinstance(Map[i], Shop):
                positions["Shop"].append(i)
            elif isinstance(Map[i], ChestGen):
                positions["ChestGen"].append(i)
            elif isinstance(Map[i], Blacksmith):
                positions["Blacksmith"].append(i)
            elif isinstance(Map[i], Boss):
                positions["Boss"].append(i)
        self.draw_base(positions)

    def draw_base(self, positions):
        self.base = Image.new("RGB", (800, 700), "white")
        draw = ImageDraw.Draw(self.base)

        draw.line((150,  50, 650,  50), fill="black", width=5)
        draw.line((150, 190, 650, 190), fill="black", width=5)
        draw.line((150, 330, 650, 330), fill="black", width=5)
        draw.line((150, 470, 650, 470), fill="black", width=5)

        draw.line((650,  50, 650, 190), fill="black", width=5)
        draw.line((150, 190, 150, 330), fill="black", width=5)
        draw.line((650, 330, 650, 470), fill="black", width=5)

        draw.ellipse((100, 25, 150, 75), outline=(0, 0, 0), width=3)

        shop_cyan = (21, 255, 255)
        blacksmith_green = (29, 171, 71)
        chest_orange = (241, 152, 26)
        enemy_red = (217, 38, 44)

        for pos in range(1, 41):
            if pos in positions["Boss"]:
                color = "yellow"
            elif pos in positions["Blacksmith"]:
                color = blacksmith_green
            elif pos in positions["Shop"]:
                color = shop_cyan
            elif pos in positions["ChestGen"]:
                color = chest_orange
            else:
                color = enemy_red

            if pos == 10:
                draw.ellipse((650-25, 120-25, 650+25, 120+25), fill=color, outline=(0, 0, 0), width=3)
            elif pos == 20:
                draw.ellipse((150-25, 260-25, 150+25, 260+25), fill=color, outline=(0, 0, 0), width=3)
            elif pos == 30:
                draw.ellipse((650-25, 400-25, 650+25, 400+25), fill=color, outline=(0, 0, 0), width=3)
            elif pos == 40:
                draw.ellipse((100, 470-25, 150, 470+25), fill=color, outline=(0, 0, 0), width=3)
            else:
                h, v = pos%10, pos//10
                if v % 2:
                    h = 10-h
                left_up = (150 + 53*h - 30, 50 + 140*v - 15)
                right_low = (150 + 53*h, 50 + 140*v + 15)
                draw.ellipse([left_up, right_low], fill=color, outline=(0, 0, 0), width=3)

            # add legend at the bottom
        draw.ellipse((40, 600, 60, 620), fill=(255,255,255), outline=(0, 0, 0), width=3)
        draw.ellipse((40, 630, 60, 650), fill=enemy_red, outline=(0, 0, 0), width=3)
        draw.ellipse((40, 660, 60, 680), fill="yellow", outline=(0, 0, 0), width=3)
        draw.ellipse((220, 600, 240, 620), fill=chest_orange, outline=(0, 0, 0), width=3)
        draw.ellipse((220, 630, 240, 650), fill=blacksmith_green, outline=(0, 0, 0), width=3)
        draw.ellipse((220, 660, 240, 680), fill=shop_cyan, outline=(0, 0, 0), width=3)
        
        draw.text((60 + 10, 600), "Start", font=self.font, fill=(0,0,0))
        draw.text((60 + 10, 630), "Enemy", font=self.font, fill=(0,0,0))
        draw.text((60 + 10, 660), "Boss", font=self.font, fill=(0,0,0))

        draw.text((240 + 10, 600), "Treasure Chest", font=self.font, fill=(0,0,0))
        draw.text((240 + 10, 630), "Blacksmith", font=self.font, fill=(0,0,0))
        draw.text((240 + 10, 660), "Shop", font=self.font, fill=(0,0,0))

    def show(self):
        self.base.show()
    def draw_players(self, players):
        image = self.base.copy()
        draw = ImageDraw.Draw(image)
        player_pos = [0]*41
        
        for i in range(len(players)):
            player = players[i]
            color = self.colors[i]
            h, v = player.pos%10, player.pos//10

            if h == 0:
                if v == 0:
                    left_up = (75, 25 + 25*player_pos[player.pos])
                    right_low = (95, 45 + 25*player_pos[player.pos])
                elif v == 4:
                    left_up = (75, 25 + 420 + 25*player_pos[player.pos])
                    right_low = (95, 45 + 420 + 25*player_pos[player.pos])
                elif v == 1 or v == 3:
                    left_up = (680, -35 + 140*v + 25*player_pos[player.pos])
                    right_low = (700, -15 + 140*v + 25*player_pos[player.pos])
                else:
                    left_up = (100, -35 + 140*v + 25*player_pos[player.pos])
                    right_low = (120, -15 + 140*v + 25*player_pos[player.pos])
            else:
                if v % 2:
                    h = 10-h
                left_up = (150 + 53*h - 25, 50 + 140*v + 20 + 25*player_pos[player.pos])
                right_low = (150 + 53*h - 5, 50 + 140*v + 40 + 25*player_pos[player.pos])
            draw.rounded_rectangle([left_up, right_low], fill=color, outline=(0, 0, 0), width=2, radius=3)
            text = player.name[0]
            text_sz = self.font.getmask(text).getbbox()
            draw.text((left_up[0] + 10 - (text_sz[2]-text_sz[0])//2, left_up[1]), text, font=self.font, fill=(255,255,255))
            player_pos[player.pos] += 1

            # draw legend
            draw.rounded_rectangle((420 + 180*(i//3), 600 + 30*(i%3), 440 + 180 * (i//3), 620 + 30*(i%3)), fill=color, outline=(0, 0, 0), width=2, radius=3)
            
            name = player.name[:16]
            suffix = ""
            if len(player.name) > 16:
                suffix = "..."
            text_sz = self.font.getmask(name+suffix).getbbox()
            while text_sz[2] - text_sz[0] >= 150:
                name = name[:-1]
                text_sz = self.font.getmask(name+suffix).getbbox()
            draw.text((440 + 10 + 180*(i//3), 600 + 30*(i%3)), name+suffix, font=self.font, fill=(0,0,0))
        return image