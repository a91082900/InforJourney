import random
from Events import Shop, Blacksmith
from Data import Bosses, BossDropItem
from Entity import Boss
from Gen import ChestGen, MonsterGen
from Data import Positions

def GenMap():
    Map = [None for i in range(41)]
    l = list(range(41))
    for i in Positions["Boss"]:
        l.remove(i)
        Map[i] = Boss(*Bosses[i//10-1][0:6], BossDropItem[i//10-1])

    for i in Positions["Shop"]:
        l.remove(i)
        Map[i] = Shop(i//10)
        
    for i in Positions["Blacksmith"]:
        l.remove(i)
        Map[i] = Blacksmith(i//10)

    for i in Positions["ChestGen"]:
        l.remove(i)
        Map[i] = ChestGen()
    for i in l: # MonsterGen
        Map[i] = MonsterGen()

    # shuffle the map
    for i in range(4):
        Map[10*i+1:10*i+10] = random.sample(Map[10*i+1:10*i+10], 9)
    return Map