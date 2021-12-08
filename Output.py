from abc import ABC, abstractmethod
from Player import Player
from Data import *
from time import sleep
from io import BytesIO

def sending(func):
    def self_catcher(*args, **kwargs):
        if not isinstance(args[0], Output):
            raise TypeError("@sending should only be used on Output instance functions")

        t = type(args[0])
        @t.sending_decorator
        def runner():
            return func(*args, **kwargs)
        
        return runner()

    return self_catcher

class Output(ABC):
    @staticmethod
    @abstractmethod
    def BadRequest() -> type:
        pass
    
    def __init__(self, bot, id, gid): #, decorator):
        self.bot = bot
        self.id = id
        self.end_markup = self.gen_inline_keyboard_markup(inline_keyboard=[
            [self.gen_inline_keyboard_button(text='Leave', callback_data=f'end {gid}')],
        ])
        # print("calling Output.__init__")
        # for name in dir(self):
        #     if name.startswith("send") or name.startswith("stat"):
        #         setattr(self, name, decorator(getattr(self, name)))

    @abstractmethod
    def _send_message():
        pass

    @abstractmethod
    def _edit_message_text():
        pass

    @staticmethod
    @abstractmethod
    def sending_decorator(func):
        pass

    @staticmethod
    @abstractmethod
    def gen_inline_keyboard_markup():
        pass
    
    @staticmethod
    @abstractmethod
    def gen_inline_keyboard_button():
        pass

    @abstractmethod
    def _send_photo():
        pass

    @sending
    def send_help(self):
        helpString = "join - Join a game\n" + \
            "start - Start a game\n" + \
            "jizz - Throw a die to move\n" + \
            "map - Show the game map\n" + \
            "pos - Show Your positon\n" + \
            "buy - [no] Buy an item in shop\n" + \
            "upgrade - [weapon/armor] Upgrade weapon or armor in blacksmith shop\n" + \
            "change - Change weapon or armor\n" + \
            "end - Leave shop or blacksmith shop\n" + \
            "drink - [no] Drink a potion\n" + \
            "mystat - Show your status\n" + \
            "showpotion - Show all your potions\n" + \
            "showstat - Show status of chosen entity\n" + \
            "retire - retire from game\n" + \
            "help - Show game help\n"
        self._send_message(self.id, helpString)

    @sending
    def send_welcome(self, name):
        self._send_message(self.id, f"{name}加入了遊戲", parse_mode="Markdown")

    @sending
    def send_start_game(self):
        self._send_message(self.id, "遊戲已開始")

    def tag_user(self, player):
        if player.username:
            return f"@{player.username}"
        else:
            return f"[{player.name}](tg://user?id={player.id})"

    @sending
    def send_player_turn_start(self, player: Player):
        self._send_message(self.id, 
            f"換{player.name}了唷 {self.tag_user(player)}\n你目前在第{player.pos}格", 
            parse_mode="Markdown"
        )
    
    @sending
    def send_jizz_result(self, player_name, jizz):
        self._send_message(self.id, f"{player_name}骰出了{jizz}.")
    
    @sending
    def send_map(self):
        self._send_photo(self.id, open("./Img/raw_map.jpg","rb"))

    @sending
    def send_painted_map(self, image):
        bio = BytesIO()
        bio.name = 'image.jpeg'
        image.save(bio, 'JPEG')
        bio.seek(0)
        self._send_photo(self.id, bio)
    
    @sending
    def send_pos(self, name, pos):
        self._send_message(self.id, f"{name}目前在第{pos}格")

    @sending
    def send_potion(self, uid, name, potions):
        potions_str = ""
        if not potions:
            potions_str = "無"
        else:
            potions_list = [f"{i}. {str(potion)}" for i, potion in enumerate(potions)]
            potions_str = "\n".join(potions_list)
        self._send_message(uid, f"{name}的藥水們:\n{potions_str}")

    @sending
    def send_heal_result(self, player: Player, potion, heal_point):
        self._send_message(self.id, f"{player.name}飲用了{potion}\n回復{heal_point}點生命\n{player.name}現在有{player.hp}點生命")

    @sending
    def send_wrong_argument(self):
        self._send_message(self.id, "參數錯誤")

    @sending
    def send_change(self, gid, name, uid, avaliable_items):
        kb_list = []
        for w in avaliable_items:
            kb_list.append([self.gen_inline_keyboard_button(text=w.name, callback_data=f"change {uid} {w.name} {gid}")])#callback_data="change "+str(uid)+" "+w.name+" "+str(gid))])

        if kb_list:
            keyboard = self.gen_inline_keyboard_markup(inline_keyboard=kb_list)
            self._send_message(self.id, f"{name}, 請選擇更換裝備", reply_markup=keyboard)
        else:
            self._send_message(self.id, f"{name}沒有可更換的裝備")

    @sending
    def change_succeed(self, name, item, identifier):
        self._edit_message_text(f"{name}已成功裝備{item}", identifier=identifier)

    @sending
    def send_retire_confirm(self, name):
        self._send_message(self.id, f"{name},你確定要退出遊戲嗎?\n確定退出請再次輸入 /retire")

    @sending
    def send_retire(self, name):
        self._send_message(self.id, f"{name}離開了遊戲")
    
    def _create_catagory_kb(self, gid):
        kb_list = [
            [self.gen_inline_keyboard_button(text="小怪", callback_data=f"showstat monster {gid}"),
            self.gen_inline_keyboard_button(text="首領", callback_data=f"showstat boss {gid}")],
            [self.gen_inline_keyboard_button(text="玩家", callback_data=f"showstat player {gid}"),
            self.gen_inline_keyboard_button(text="武器", callback_data=f"showstat weapon 0 {gid}")],
            [self.gen_inline_keyboard_button(text="防具", callback_data=f"showstat armor 0 {gid}"),
            self.gen_inline_keyboard_button(text="道具", callback_data=f"showstat item {gid}")]
        ]
        return self.gen_inline_keyboard_markup(inline_keyboard=kb_list)

    @sending
    def send_stat(self, gid, uid):
        # kb_list = [
        #     [self.gen_inline_keyboard_button(text="小怪", callback_data=f"showstat monster {gid}"),
        #     self.gen_inline_keyboard_button(text="首領", callback_data=f"showstat boss {gid}")],
        #     [self.gen_inline_keyboard_button(text="玩家", callback_data=f"showstat player {gid}"),
        #     self.gen_inline_keyboard_button(text="武器", callback_data=f"showstat weapon 0 {gid}")],
        #     [self.gen_inline_keyboard_button(text="防具", callback_data=f"showstat armor 0 {gid}"),
        #     self.gen_inline_keyboard_button(text="道具", callback_data=f"showstat item {gid}")]
        # ]
        # keyboard = self.gen_inline_keyboard_markup(inline_keyboard=kb_list)
        self._send_message(uid, "請選擇種類", reply_markup=self._create_catagory_kb(gid))

    @sending
    def stat_category(self, gid, identifier):
        # kb_list = [
        #     [self.gen_inline_keyboard_button(text="小怪", callback_data="showstat monster"),
        #     self.gen_inline_keyboard_button(text="首領", callback_data="showstat boss")],
        #     [self.gen_inline_keyboard_button(text="玩家", callback_data="showstat player"),
        #     self.gen_inline_keyboard_button(text="武器", callback_data="showstat weapon 0")],
        #     [self.gen_inline_keyboard_button(text="防具", callback_data="showstat armor 0"),
        #     self.gen_inline_keyboard_button(text="道具", callback_data="showstat item")]
        # ]
        # keyboard = self.gen_inline_keyboard_markup(inline_keyboard=kb_list)
        self._edit_message_text("請選擇種類", identifier=identifier, reply_markup=self._create_catagory_kb(gid))

    @sending
    def stat_monster_stage(self, gid, identifier):
        kb_list = []
        for i in range(4):
            kb_list.append([self.gen_inline_keyboard_button(text=f"階段{i+1}", callback_data=f"showstat monster {i} {gid}")])
        kb_list.append([self.gen_inline_keyboard_button(text="上一層", callback_data=f"showstat {gid}")])
        keyboard = self.gen_inline_keyboard_markup(inline_keyboard=kb_list)
        self._edit_message_text("請選擇", identifier=identifier, reply_markup=keyboard)

    @sending
    def stat_monsters(self, gid, identifier, stage):
        kb_list = []
        display = list(Monsters[stage])
        for name1, name2 in zip(display[::2], display[1::2]):
            kb_list.append([
                self.gen_inline_keyboard_button(text=name1, callback_data=f"showstat monster {stage} {name1} {gid}"), 
                self.gen_inline_keyboard_button(text=name2, callback_data=f"showstat monster {stage} {name2} {gid}")
            ])
        if len(display) % 2:
            kb_list.append([self.gen_inline_keyboard_button(text=display[-1], callback_data=f"showstat monster {stage} {display[-1]} {gid}")])
        kb_list.append([self.gen_inline_keyboard_button(text="上一層", callback_data=f"showstat monster {gid}")])
        keyboard = self.gen_inline_keyboard_markup(inline_keyboard=kb_list)
        self._edit_message_text("請選擇", identifier=identifier, reply_markup=keyboard)

    @sending
    def stat_bosses(self, gid, identifier):
        kb_list = []
        for i in range(4):
            kb_list.append([self.gen_inline_keyboard_button(text=Bosses[i][0], callback_data=f"showstat boss {i} {gid}")])
        kb_list.append([self.gen_inline_keyboard_button(text="上一層", callback_data=f"showstat {gid}")])
        keyboard = self.gen_inline_keyboard_markup(inline_keyboard=kb_list)
        self._edit_message_text("請選擇", identifier=identifier, reply_markup=keyboard)

    @sending
    def stat_players(self, gid, players, identifier):
        kb_list = []
        for player in players:
            kb_list.append([self.gen_inline_keyboard_button(text=player.name, callback_data=f"showplayer {player.id} {gid}")])
        kb_list.append([self.gen_inline_keyboard_button(text="上一層", callback_data=f"showstat {gid}")])
        keyboard = self.gen_inline_keyboard_markup(inline_keyboard=kb_list)
        self._edit_message_text("請選擇", identifier=identifier, reply_markup=keyboard)

    @sending
    def stat_items(self, gid, identifier):
        kb_list = []
        for p in Potions:
            kb_list.append([self.gen_inline_keyboard_button(text=p, callback_data=f"showstat item {p} {gid}")])
        kb_list.append([self.gen_inline_keyboard_button(text="上一層", callback_data=f"showstat {gid}")])
        keyboard = self.gen_inline_keyboard_markup(inline_keyboard=kb_list)
        self._edit_message_text("請選擇", identifier=identifier, reply_markup=keyboard)

    @sending
    def stat_weapons(self, gid, identifier, page):
        kb_list = []
        weapon_list = list(Weapons.items())
        if page:
            kb_list.append([self.gen_inline_keyboard_button(text="<<", callback_data=f"showstat weapon {page-1} {gid}")])

        display = weapon_list[page*6:min(page*6+6, len(weapon_list))]
        for item1, item2 in zip(display[::2], display[1::2]):
            kb_list.append([
                self.gen_inline_keyboard_button(text=item1[0], callback_data=f"showweapon {item1[0]} {gid}"),
                self.gen_inline_keyboard_button(text=item2[0], callback_data=f"showweapon {item2[0]} {gid}")
            ])
        if len(display) % 2:
            kb_list.append([self.gen_inline_keyboard_button(text=display[-1][0], callback_data=f"showweapon {display[-1][0]} {gid}")])
        if page*6 + 6 < len(weapon_list):
            kb_list.append([self.gen_inline_keyboard_button(text=">>", callback_data=f"showstat weapon {page+1} {gid}")])
        kb_list.append([self.gen_inline_keyboard_button(text="上一層", callback_data=f"showstat {gid}")])
        keyboard = self.gen_inline_keyboard_markup(inline_keyboard=kb_list)
        self._edit_message_text("請選擇", identifier=identifier, reply_markup=keyboard)

    @sending
    def stat_armors(self, gid, identifier, page):
        kb_list = []
        armor_list = list(Armors.items())
        if page:
            kb_list.append([self.gen_inline_keyboard_button(text="<<", callback_data=f"showstat armor {page-1} {gid}")])

        display = armor_list[page*6:min(page*6+6, len(armor_list))]
        for item1, item2 in zip(display[::2], display[1::2]):
            kb_list.append([
                self.gen_inline_keyboard_button(text=item1[0], callback_data=f"showarmor {item1[0]} {gid}"),
                self.gen_inline_keyboard_button(text=item2[0], callback_data=f"showarmor {item2[0]} {gid}")
            ])
        if len(display) % 2:
            kb_list.append([self.gen_inline_keyboard_button(text=display[-1][0], callback_data=f"showarmor {display[-1][0]} {gid}")])
        if page*6 + 6 < len(armor_list):
            kb_list.append([self.gen_inline_keyboard_button(text=">>", callback_data=f"showstat armor {page+1} {gid}")])
        kb_list.append([self.gen_inline_keyboard_button(text="上一層", callback_data=f"showstat {gid}")])
        keyboard = self.gen_inline_keyboard_markup(inline_keyboard=kb_list)
        self._edit_message_text("請選擇", identifier=identifier, reply_markup=keyboard)

    @sending
    def stat_player(self, uid, player: Player):
        # player_str = "{name}: 等級:{}\n攻:{}, 防:{}, \nHP: {}, 最大HP: {}\n"
        # player_str += "武器:{}\n  攻+{} 防+{}\n防具:{}\n  攻+{} 防+{}\n"
        # player_str += "{name}目前經驗值:{}\n升級所需經驗值:{}\n"
        # player_str += "{name}現在有 {} 金幣"
        print('inside stat_player')
        print('player:')
        print(player)
        player_str = (
            f'{player.name}: 等級:{player.lvl}\n'
            f'攻:{player.atk}, 防:{player.dfd}, \n'
            f'HP: {player.hp}, 最大HP: {player.maxhp}\n'
            f'武器:{player.weapon.name}\n'
            f'  攻+{player.weapon.atk} 防+{player.weapon.dfd}\n'
            f'防具:{player.armor.name}\n'
            f'  攻+{player.armor.atk} 防+{player.armor.dfd}\n'
            f'{player.name}目前經驗值:{player.exp}\n'
            f'升級所需經驗值:{Exps[player.lvl] if player.lvl < len(Exps) else "-"}\n'
            f'{player.name}現在有 {player.coin} 金幣'
        )

        self._send_message(uid, player_str)
    
    @sending
    def stat_monster(self, uid, monster_name, monster_data):
        self._send_message(uid, (
            f'{monster_name}: 攻:{monster_data[0]}, 防:{monster_data[1]}, HP: {monster_data[2]}\n'
            f'經驗值: {monster_data[3]}, 金幣: {monster_data[4]}\n'
            f'出現等級: {monster_data[5]} ~ {monster_data[6]}'
        ))

    @sending
    def stat_item(self, uid, potion):
        self._send_message(uid, f'恢復{"/".join(map(lambda x: str(x), potion))}點生命')

    @sending
    def stat_weapon(self, uid, weapon):
        (atk, dfd) = Weapons[weapon]
        self._send_message(uid, f"{weapon}:\n攻:{atk} 防:{dfd}")

    @sending
    def stat_armor(self, uid, armor):
        (atk, dfd) = Armors[armor]
        self._send_message(uid, f"{armor}:\n攻:{atk} 防:{dfd}")

    @sending
    def send_upgrade_limited(self, upgrade_times):
        self._send_message(self.id, f"金幣不足 共升級{upgrade_times}次")

    @sending
    def send_upgrade_full(self, upgrade_times):
        self._send_message(self.id, f"升級{upgrade_times}次成功")

    @abstractmethod
    def _editable_send(self, content, message):
        try:
            if message == None:
                print("message is None")
            if not message:
                return self._send_message(self.id, content)
            return self._edit_message_text(f"{message.text}\n{content}", message=message)
        except self.BadRequest():
            print("Bad request error")
            return message

    @sending
    def send_meet(self, name, enemy, event_name, message = None):
        return self._editable_send(f"{name}遇到了{enemy} {event_name}", message)

    @sending
    def send_fight_result(self, res, message = None):
        return self._editable_send(res, message)

    @sending
    def send_beat(self, winner, loser, coin = None, exp = None, message = None):
        content = f"{winner}打倒了{loser}"
        if coin and exp:
            content += f" ，獲得了{coin}金幣和{exp}經驗值"
        return self._editable_send(content, message)

    @sending
    def send_beaten(self, loser, winner, message = None):
        return self._editable_send(f"{loser}被{winner}打倒了 SAD", message)

    @sending
    def send_tie(self, message = None):
        return self._editable_send("竟然是百年難得一見的平手", message)

    @sending
    def send_congrats_clear(self, name, message = None):
        return self._editable_send(f"恭喜{name}通關遊戲", message)
    
    @sending
    def send_last_strike(self, name, drop_weapon_name, drop_armor_name, message = None):
        return self._editable_send(f"{name}獲得最後一擊獎勵: {drop_weapon_name}, {drop_armor_name}", message)
    
    @sending
    def send_reach_shop(self, name, message = None):
        return self._editable_send(f"{name}抵達一間商店", message)

    def chinese(self, data):
        count = 0
        for s in data:
            if ord(s) > 127:
                count += 1
        return count

    @sending
    def send_shop_items(self, goods, price, message = None):
        msg = "```\n======歡迎來到商店======\n"
        for i, (item, price) in enumerate(zip(goods,price)):
            msgstr = '{0:{wd}}'.format(item.name,wd=15-self.chinese(item.name))
            msg+= "{}. {}{:>5}\n".format(i,msgstr,price)
        msg+="```"
        if not message:
            return self._send_message(self.id, msg, parse_mode="Markdown", reply_markup=self.end_markup)
        return self._edit_message_text(f"{message.text}\n{msg}", message=message, parse_mode="Markdown", reply_markup=self.end_markup)

    @sending
    def send_reach_blacksmith(self, name, message = None):
        return self._editable_send(f"{name}抵達一間鐵匠鋪", message)

    @sending
    def send_blacksmith_service(self, upgrade, weapon_cost, armor_cost, message = None):
        content = ("\n"
               f"武器升級 攻防+{upgrade} 價格:{weapon_cost}金幣\n\n"
               f"防具升級 攻防+{upgrade} 價格:{armor_cost}金幣\n"
        )
        if not message:
            return self._send_message(self.id, content, reply_markup=self.end_markup)
        return self._edit_message_text(f"{message.text}\n{content}", message=message, parse_mode="Markdown", reply_markup=self.end_markup)

    @sending
    def send_find_chest(self, name, coin, weapon_name = None, message = None):
        content = f"{name}在一個寶箱裡找到了 {coin} 金幣"
        if weapon_name:
            content += f"和一個{weapon_name}"
        return self._editable_send(content, message)

    @sending
    def send_level_up(self, name, lvl, message = None):
        return self._editable_send(f"{name}升到了{lvl}級喔喔喔喔喔", message)

    @sending
    def send_not_enough_coin(self):
        self._send_message(self.id, "金幣不足 購買失敗")

    @sending
    def send_buy_success(self):
        self._send_message(self.id, "購買成功")

    @sending
    def send_end_game(self):
        self._send_message(self.id, "遊戲已結束")

    def direct_from_in(self, game, query_data, uid, identifier):
        try:
            if query_data[0] == "change" and len(query_data) > 2:
                if uid == int(query_data[1]):
                    game.request_change(uid, query_data[2], identifier)
                else:
                    print(uid, query_data)
            elif query_data[0] == "end":
                game.request_end(uid)
            elif query_data[0] == "showstat":
                try:
                    if len(query_data) > 3:
                        if query_data[1] == "monster":
                            game.show_monster(uid, query_data[3], Monsters[int(query_data[2])][query_data[3]])
                    if len(query_data) > 2:
                        if query_data[1] == "monster":
                            i = int(query_data[2])
                            self.stat_monsters(game.id, identifier, i)
                        elif query_data[1] == "weapon":
                            start = int(query_data[2])
                            self.stat_weapons(game.id, identifier, start)
                        elif query_data[1] == "armor":
                            start = int(query_data[2])
                            self.stat_armors(game.id, identifier, start)
                        elif query_data[1] == "boss":
                            i = int(query_data[2])
                            game.show_monster(uid, Bosses[i][0], Bosses[i][1:])
                        elif query_data[1] == "item":
                            if query_data[2] in Potions:
                                potion = Potions[query_data[2]]
                                self.stat_item(uid, potion)
                    elif len(query_data) > 1:
                        if query_data[1] == "player":
                            self.stat_players(game.id, game.get_players(), identifier)
                        elif query_data[1] == "boss":
                            self.stat_bosses(game.id, identifier)
                        elif query_data[1] == "item":
                            self.stat_items(game.id, identifier)
                        elif query_data[1] == "monster":
                            self.stat_monster_stage(game.id, identifier)
                    else:
                        self.stat_category(game.id, identifier)
                except:
                    pass
            elif query_data[0] == "showplayer" and len(query_data)>1:
                try:
                    show_player_id = int(query_data[1])
                    game.request_show_player(uid, show_player_id)
                except:
                    pass
            elif query_data[0] == "showweapon" and len(query_data)>1:
                self.stat_weapon(uid, query_data[1])
            elif query_data[0] == "showarmor" and len(query_data)>1:
                self.stat_armor(uid, query_data[1])
        except:
            pass