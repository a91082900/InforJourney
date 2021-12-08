from enum import Enum
from typing import Dict
from time import sleep
from random import randint
from num2words import num2words
from MapPainter import MapPainter

from Output import Output
from Map import GenMap
from Data import Pending
from Player import Player

class State(Enum):
    UNSTARTED = 0
    STARTED = 1
    PENDING = 2
    EVENT = 3
    END = 4
    ERROR = -1

class Not:
    def __init__(self, state: State):
        self.state = state

def available_in_states(*states):
    def decorator(func):
        def state_check(*args, **kwargs):
            for state in states:
                if isinstance(state, State):
                    if args[0].state == state:
                        return func(*args, **kwargs)
                elif isinstance(state, Not):
                    if args[0].state != state.state:
                        return func(*args, **kwargs)
                else:
                    raise ValueError("require_game_state only accept argument of type State or Not")
        return state_check
    
    return decorator





class Game:
    def __init__(self, groupid, out: Output):
        self.Map = GenMap()
        self.id = groupid
        self.ids = {}
        self.players = []
        self.state = State.UNSTARTED
        self.now_player_no = -1
        self.out = out
        self.map_painter = MapPainter(Map=self.Map)

    def now_player(self) -> Player:
        return self.players[self.now_player_no]

    @available_in_states(State.UNSTARTED)
    def on_start(self):
        self.start()

    @available_in_states(Not(State.UNSTARTED))
    def on_map(self):
        self.out.send_map()
    
    @available_in_states(Not(State.UNSTARTED))
    def on_pos(self, uid):
        self.out.send_pos(self.ids[uid].name, self.ids[uid].pos)
    
    @available_in_states(State.PENDING)
    def on_jizz(self, uid, moves = None):
        if self.now_player().id == uid:
            self.move(self.now_player(), moves)

    @available_in_states(State.EVENT)
    def on_upgrade(self, uid, item, time):
        if self.now_player().id == uid and \
            self.now_player().pending == Pending.BLACKSMITH:
            self.now_player().upgrade(item, self.out, time)

    @available_in_states(State.EVENT)
    def on_buy(self, uid, item_no):
        if self.now_player().id == uid and self.now_player().pending == Pending.SHOP:
            self.now_player().purchase(item_no, self.out)

    @available_in_states(Not(State.UNSTARTED))
    def on_mystat(self, uid):
        self.show_player(uid, self.ids[uid])
    
    @available_in_states(State.EVENT)
    def on_end(self, uid):
        if self.now_player().id == uid and self.now_player().pending != Pending.CHANGE:
            self.end()

    @available_in_states(Not(State.UNSTARTED))
    def on_help(self):
        self.out.send_help()

    @available_in_states(Not(State.UNSTARTED))
    def on_show_potion(self, uid):
        self.out.send_potion(uid, self.ids[uid].name, self.ids[uid].potions)

    @available_in_states(State.PENDING)
    def on_drink(self, uid, potion_index):
        if self.now_player().id == uid:
            self.drink(self.now_player(), potion_index)
    
    def on_join(self, uid, name, username):
        if self.state == State.UNSTARTED:
            if uid not in self.ids:
                self.players.append(Player(uid, name, username))
                self.ids.update({uid : self.players[-1]})
                self.out.send_welcome(name)
                if len(self.players) == 4:
                    self.start()
        else:
            if len(self.players) < 4 and uid not in self.ids:
                self.players.append(Player(uid, name, username))
                self.ids.update({uid : self.players[-1]})
                self.out.send_welcome(name)
        
    @available_in_states(Not(State.UNSTARTED))
    def on_change(self, uid):
        self.out.send_change(self.id, self.ids[uid].name, uid, self.ids[uid].unused_weapons + self.ids[uid].unused_armors)
    
    @available_in_states(Not(State.UNSTARTED))
    def on_retire(self, uid):
        if self.ids[uid].pending != Pending.RETIRE:
            self.out.send_retire_confirm(self.ids[uid].name)
            self.ids[uid].pending = Pending.RETIRE
        else:
            self.out.send_retire(self.ids[uid].name)
            idx = self.players.index(self.ids[uid])
            self.players.pop(idx)
            del self.ids[uid]
            if len(self.players) == 0:
                self.endgame()
                return
            if idx < self.now_player_no:
                self.now_player_no -= 1
            elif idx == self.now_player_no:
                self.next_player()

    @available_in_states(Not(State.UNSTARTED))
    def on_show_stat(self, uid):
        self.out.send_stat(self.id, uid)
        stat_ids[uid] = self

    def passage(self, *args, **kwargs):
        self.out.direct_from_in(self, *args, **kwargs)

    def request_change(self, uid, item_name, identifier):
        changed = self.ids[uid].change2(item_name)
        if changed:
            print("change called")
            self.out.change_succeed(self.ids[uid].name, changed, identifier)
        else:
            print("change failed")

    def request_end(self, uid):
        if self.state == State.EVENT and self.now_player().id == uid:
            self.end()

    def get_players(self):
        return self.players
    
    def request_show_player(self, uid, show_player_id):
        self.show_player(uid, self.ids[show_player_id])
       
    def show_player(self, uid, entity):
        print('showing')
        print(entity)
        self.out.stat_player(uid, entity)
    def show_monster(self, uid, name, monster_data):
        self.out.stat_monster(uid, name, monster_data)
    def start(self):
        if len(self.players) == 0:
            return
        self.state = State.STARTED
        self.out.send_start_game()
        self.next_player() 
    def end(self):
        sleep(2) # sleep 3 sec for reduce loding
        self.now_player().on_hand.clear()
        self.next_player()
    
    def next_player(self):
        self.now_player_no = (self.now_player_no + 1) % len(self.players)
        self.state = State.PENDING
        self.out.send_player_turn_start(self.now_player())
    
    def move(self, player, moved):
        self.state = State.EVENT
        if not isinstance(moved, int):
            moved = randint(1, 4)
        self.out.send_jizz_result(player.name, num2words(moved))
        player.move(moved)
        for other_player in self.players:
            if other_player is not player:
                if other_player.pos == player.pos:
                    player.meet(other_player, self.out)
        if self.Map[player.pos] is not None:
            meet = player.meet(self.Map[player.pos], self.out, True)
            if isinstance(meet, str):
                self.endgame()
            elif meet:
                self.end()
        else:
            self.end()
    def drink(self, player, i):
        self.out.send_heal_result(player, player.potions[i], player.potions[i].drink(player))
        player.potions.pop(i)
    def endgame(self):
        self.out.send_end_game()
        game_stat_ids = [k for k,v in stat_ids.items() if v == self]
        for k in game_stat_ids:
            del stat_ids[k]
        self.__init__(self.id, self.out)

    @available_in_states(Not(State.UNSTARTED))
    def on_draw_map(self):
        painted = self.map_painter.draw_players(self.players)
        self.out.send_painted_map(painted)

#user_id -> the game they're questing
stat_ids: Dict[int, Game] = dict()