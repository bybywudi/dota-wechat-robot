import dota2api
from wechat_sender import Sender
import time
from wxpy import *
import json
import requests
import datetime

players = {134976802: '白杨', 194765012: '李明昊', 163287641: 'P酱', 137479998: '涛神', 397440385: '亮亮', 144128282: '肥导', 142874459: '冯帆', 135885299: '蛋酱', 189119223: '高远见', 307998042: '头娃', 163338929: '航儿', 139095627: '刘洋'}
with open("./hero_names.json",'r') as hero_names_f:
    hero_names = json.load(hero_names_f)

sender = Sender(token='test')
key = "C1117CC15AFE30841DF863B901A0D35A"
domain = "wxdotarobot"

api = dota2api.Initialise(key)
heroes = api.get_heroes()
refresh_sencond = 300
#match = api.get_match_details(match_id=5668508119)
#player_matches = api.get_match_history(134976802)


def get_hero_by_id(id):
    for item in heroes['heroes']:
        if id == item['id']:
            return item['localized_name']

def send_player_latest_game_data(id):
    data = get_player_latest_game_data(id)
    match_res = ""
    if hero_names.get(data['hero_name']):
        data['hero_name'] = hero_names.get(data['hero_name'])
    if data['win'] == 1:
        match_res = ",并取得了胜利"
    else:
        match_res = ",但是失败了"
    res = "DOTA机器人消息：" + str(get_player_name_by_id(id)) + "在最近的一场比赛中使用了" + str(data['hero_name']) + match_res \
          + ",KDA是：" + str(data['kills']) + "/" + str(data['deaths']) + "/" + str(data['assists']) + ",造成了" + str(data['hero_damage']) + "点英雄伤害,结论：" + str(get_match_detail_conclusion(data))
    sender.send(str(res))

def get_player_latest_game_conclusion(id):
    data = get_player_latest_game_data(id)
    match_res = ""
    if hero_names.get(data['hero_name']):
        data['hero_name'] = hero_names.get(data['hero_name'])
    if data['win'] == 1:
        match_res = ",并取得了胜利"
    else:
        match_res = ",但是失败了"
    res = "DOTA机器人消息：" + str(get_player_name_by_id(id)) + "在最近的一场比赛中使用了" + str(data['hero_name']) + match_res \
          + ",KDA是：" + str(data['kills']) + "/" + str(data['deaths']) + "/" + str(data['assists']) + ",造成了" + str(data['hero_damage']) + "点英雄伤害,分析一下：" + str(get_match_detail_conclusion(data))
    return res, data

def get_player_name_by_id(id):
    return players[id]

def get_player_latest_game_data(id):
    data = {}
    data['order'] = 1
    data['has_by'] = False
    data['has_lmh'] = False
    data['has_pj'] = False
    data['has_ts'] = False
    data['has_ll'] = False
    data['has_fd'] = False
    data['has_ff'] = False
    data['has_dj'] = False
    data['has_gyj'] = False
    data['has_tw'] = False
    data['has_hang'] = False
    data['has_ly'] = False
    match = get_player_latest_match(id)
    data['match_id'] = match['match_id']
    players = match['players']
    dire_total_damage = 0
    radiant_total_damage = 0
    dire_total_tower_damage = 0
    radiant_total_tower_damage = 0
    j = 0
    for p in players:
        j = j + 1
        if 1<=j<=5:
            radiant_total_damage = radiant_total_damage + p['hero_damage']
            radiant_total_tower_damage = radiant_total_tower_damage + p['tower_damage']
        else:
            dire_total_damage = dire_total_damage + p['hero_damage']
            dire_total_tower_damage = dire_total_tower_damage + p['tower_damage']
        if p['account_id'] == 134976802:
            data['has_by'] = True
        if p['account_id'] == 194765012:
            data['has_lmh'] = True
        if p['account_id'] == 163287641:
            data['has_pj'] = True
        if p['account_id'] == 137479998:
            data['has_ts'] = True
        if p['account_id'] == 397440385:
            data['has_ll'] = True
        if p['account_id'] == 144128282:
            data['has_fd'] = True
        if p['account_id'] == 142874459:
            data['has_ff'] = True
        if p['account_id'] == 135885299:
            data['has_dj'] = True
        if p['account_id'] == 189119223:
            data['has_gyj'] = True
        if p['account_id'] == 307998042:
            data['has_tw'] = True
        if p['account_id'] == 163338929:
            data['has_hang'] = True
        if p['account_id'] == 139095627:
            data['has_ly'] = True
    i = 0
    for p in players:
        i = i + 1
        if p['account_id'] == id:
            if 1<=i<=5:
                data['camp'] = 'radiant'
            else:
                data['camp'] = 'dire'
            if match['radiant_win'] == True and data['camp'] == 'radiant':
                data['win'] = 1
            elif match['radiant_win'] == False and data['camp'] == 'dire':
                data['win'] = 1
            else:
                data['win'] = 0
            data['kills'] = p['kills']
            data['gold'] = p['gold']
            data['assists'] = p['assists']
            data['deaths'] = p['deaths']
            if p.__contains__('hero_name'):
                data['hero_name'] = p['hero_name']
            else:
                data['hero_name'] = get_hero_by_id(p['hero_id'])
            data['hero_damage'] = p['hero_damage']
            data['duration'] = match['duration']
            data['endtime'] = match['start_time'] + match['duration']
            if data['camp'] == 'radiant':
                data['battle_rate'] = float((data['kills'] + data['assists']) / match['radiant_score'])
                data['death_rate'] = float(data['deaths'] / match['dire_score'])
                data['hero_damage_rate'] = float(p['hero_damage'] / radiant_total_damage)
                data['tower_damage_rate'] = float(p['tower_damage'] / radiant_total_tower_damage)
            else:
                data['battle_rate'] = float((data['kills'] + data['assists']) / match['dire_score'])
                data['death_rate'] = float(data['deaths'] / match['radiant_score'])
                data['hero_damage_rate'] = float(p['hero_damage'] / dire_total_damage)
                data['tower_damage_rate'] = float(p['tower_damage'] / dire_total_tower_damage)
            try:
                for pb in match['picks_bans']:
                    if pb['hero_id'] == p['hero_id']:
                        data['order'] = pb['order'] + 1
                        break
            except:
                pass
            data['dire_score'] = match['dire_score']
            data['radiant_score'] = match['radiant_score']
            data['gpm'] = p['gold_per_min']
            data['xpm'] = p['xp_per_min']
            data['denies'] = p['denies']
            data['tower_damage'] = p['tower_damage']
            data['hero_healing'] = p['hero_healing']
            return data


def get_player_latest_match(id):
    latest_matches = api.get_match_history(id)
    for m in latest_matches['matches']:
        return api.get_match_details(match_id=m['match_id'])

def get_player_latest_days_match(id, date):
    rsp = requests.get("https://api.opendota.com/api/players/" + str(id) + "/matches?api_key=" + key + "&date=" + str(date))
    if rsp.status_code == 200:
        rspJson = json.loads(rsp.text)
        return rspJson
    else:
        return -1

def get_all_player_latest_days_match(date):
    s = requests.Session()
    data = {}
    for p in players.keys():
        rsp = s.get("https://api.opendota.com/api/players/" + str(p) + "/matches?api_key=" + key + "&date=" + str(date))
        if rsp.status_code == 200:
            rspJson = json.loads(rsp.text)
            data[p] = rspJson
        else:
            print("error")
    return data

def get_match_conclusion(mdata):
    kda = (mdata['kills'] + mdata['assists']) / mdata['deaths']
    if mdata['win'] == 1:
        if kda >= 6:
            return "血妈Carry"
        if 4 <= kda < 6:
            return "比较Carry"
        if 3 <= kda < 4:
            return "中规中矩"
        if 2 <= kda < 3:
            return "稍微有点躺"
        if 0 <= kda < 2:
            return "纯躺"
    elif mdata['win'] == 0:
        if kda >= 6:
            return "带不动队友"
        if 4 <= kda < 6:
            return "虽败犹荣"
        if 2 <= kda < 4:
            return "尽力了"
        if 1.5 <= kda < 2:
            return "菜的扣脚"
        if 0 <= kda < 1.5:
            return "被打的烂中爆烂"
    else:
        return "难以形容"

def get_match_detail_conclusion(mdata):
    kda = (mdata['kills'] + mdata['assists']) / mdata['deaths']
    gmp_damage_rate = mdata['hero_damage_rate'] / mdata['gpm']
    total_c = ""
    kda_c = ""
    damage_rate_c = ""
    tower_damage_rate_c = ""
    battle_rate_c = ""
    pick_order_c = ""
    gpm_c = ""
    xpm_c = ""
    damage_and_gpm_rate_c = ""
    duration_c = ""
    score_c = ""
    if mdata['win'] == 1:
        if kda >= 6:
            kda_c = "血妈Carry"
        if 4 <= kda < 6:
            kda_c = "比较Carry"
        if 3 <= kda < 4:
            kda_c = "中规中矩"
        if 2 <= kda < 3:
            kda_c = "稍微有点躺"
        if 0 <= kda < 2:
            kda_c = "纯躺"
    elif mdata['win'] == 0:
        if kda >= 6:
            kda_c = "带不动队友"
        if 4 <= kda < 6:
            kda_c = "虽败犹荣"
        if 2 <= kda < 4:
            kda_c = "尽力了"
        if 1.5 <= kda < 2:
            kda_c = "菜的扣脚"
        if 0 <= kda < 1.5:
            kda_c = "被打的烂中爆烂"
    else:
        kda_c = "难以形容"

    if mdata['win'] == 1:
        if mdata['order'] <= 4:
            pick_order_c = "非常的不怕针对了,就是自信"
        elif mdata['order'] > 6:
            pick_order_c = "藏到了最后，拿出了绝活，真有你的啊"
        else:
            pick_order_c = "比较求稳的"
    else:
        if mdata['order'] <= 4:
            pick_order_c = "头真铁，这么早就敢拿出来，怪不得被打的烂中爆烂"
        elif mdata['order'] > 6:
            pick_order_c = "让队友先选都赢不了，下次你第一个选"
        else:
            pick_order_c = "不是很勇敢的"

    if mdata['win'] == 1:
        if mdata['duration'] < 1500:
            duration_c = "25分钟内推平了对方，这游戏真简单"
        elif 1500 <= mdata['duration'] < 2100:
            duration_c = "打的算是有来有回了"
        elif 2100 <= mdata['duration'] < 2700:
            duration_c = "可以说是十分焦灼了"
        else:
            duration_c = "算是一场TI决赛了"
    else:
        if mdata['duration'] < 1500:
            duration_c = "25分钟内被推平了，经典节奏"
        elif 1500 <= mdata['duration'] < 2100:
            duration_c = "抵抗了几波，但是很快就输了，经典节奏"
        elif 2100 <= mdata['duration'] < 2700:
            duration_c = "还是十分交啄的，但是技不如人"
        else:
            duration_c = "TI决赛输了，恭喜OG"

    if gmp_damage_rate < 0.00033:
        damage_and_gpm_rate_c = "低的过分了"
    elif 0.000333 <= gmp_damage_rate < 0.000666:
        damage_and_gpm_rate_c = "正常水平"
    elif 0.000666 <= gmp_damage_rate < 0.000999:
        damage_and_gpm_rate_c = "比较高的"
    elif 0.000999 <= gmp_damage_rate:
        damage_and_gpm_rate_c = "高的一逼"

    if mdata['tower_damage_rate'] < 0.05:
        tower_damage_rate_c = "作为一个酱油，不敢摸塔也是正常的"
    elif 0.05 <= mdata['tower_damage_rate'] < 0.10:
        tower_damage_rate_c = "也算是摸了几下塔"
    elif 0.10 <= mdata['tower_damage_rate'] < 0.20:
        tower_damage_rate_c = "尽力了"
    elif 0.20 <= mdata['tower_damage_rate'] < 0.40:
        tower_damage_rate_c = "也是老带球王了"
    elif 0.40 <= mdata['tower_damage_rate']:
        tower_damage_rate_c = "他知道这个游戏的精髓"

    if mdata['battle_rate'] < 0.2:
        battle_rate_c = "诶？这局有我吗？"
    elif 0.2 <= mdata['battle_rate'] < 0.3:
        battle_rate_c = "全程See就是我的打法。"
    elif 0.3 <= mdata['battle_rate'] < 0.5:
        battle_rate_c = "TPCD,这波我就不来了。"
    elif 0.5 <= mdata['battle_rate'] < 0.7:
        battle_rate_c = "到处打架，我尽力了。"
    elif 0.7 <= mdata['battle_rate']:
        battle_rate_c = "每次人头都有我，还要喷？"

    total_c = "这把比赛打了" + str(datetime.timedelta(seconds=mdata['duration'])) + "，" + duration_c + "。这把他是第" + str(mdata['order']) + "手选的人,可以说是" + pick_order_c + "。从KDA来看，他是" + kda_c + "的，从经济输出比分析一下，他造成了全队" + str(float('%.3f' % (mdata['hero_damage_rate']))) + "的伤害，GPM是" + str(mdata['gpm']) + "，可以说是" + damage_and_gpm_rate_c + "。从参战数据来看，他参加了" + str(float('%.3f' % (mdata['battle_rate']))) \
              + "的战斗，应该获得称号：" + battle_rate_c + "但是DOTA是个推塔的游戏，他对建筑物造成了全队" + str(float('%.3f' % (mdata['tower_damage_rate']))) + "的伤害，可以说" + tower_damage_rate_c + "。"
    if mdata['denies'] > 15:
        total_c = total_c + "如果硬要说这把的亮点的话，就是他反补了" + str(mdata['denies']) + "个吧。"
    return total_c

def print_conclusions():
    for p in players.keys():
        try:
            print(get_player_latest_game_conclusion(p))
        except:
            print("error")
            pass

def send_all_conclusions():
    for p in players.keys():
        try:
            print("sending:" + str(p))
            send_player_latest_game_data(p)
        except:
            pass

def get_all_weekly_conclusion():
    data = get_all_player_latest_days_match(7)
    #data = {397440385: [{'kills': 3, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 18, 'duration': 2108, 'game_mode': 22, 'deaths': 3, 'hero_id': 84, 'start_time': 1603635616, 'match_id': 5671723688, 'skill': 3, 'party_size': 3, 'lobby_type': 0, 'player_slot': 131}, {'kills': 1, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 18, 'duration': 2890, 'game_mode': 3, 'deaths': 13, 'hero_id': 20, 'start_time': 1603623265, 'match_id': 5671412804, 'skill': 2, 'party_size': 5, 'lobby_type': 0, 'player_slot': 128}, {'kills': 4, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 6, 'duration': 1736, 'game_mode': 3, 'deaths': 12, 'hero_id': 26, 'start_time': 1603621266, 'match_id': 5671371804, 'skill': 2, 'party_size': 5, 'lobby_type': 0, 'player_slot': 128}, {'kills': 2, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 12, 'duration': 2609, 'game_mode': 3, 'deaths': 14, 'hero_id': 74, 'start_time': 1603617321, 'match_id': 5671293405, 'skill': 3, 'party_size': 5, 'lobby_type': 0, 'player_slot': 3}], 134976802: [{'kills': 11, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 6, 'duration': 2609, 'game_mode': 3, 'deaths': 12, 'hero_id': 67, 'start_time': 1603617321, 'match_id': 5671293405, 'skill': 3, 'party_size': 5, 'lobby_type': 0, 'player_slot': 0}, {'kills': 10, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 19, 'duration': 2689, 'game_mode': 3, 'deaths': 8, 'hero_id': 39, 'start_time': 1603614268, 'match_id': 5671231312, 'skill': 2, 'party_size': 5, 'lobby_type': 0, 'player_slot': 128}, {'kills': 13, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 14, 'duration': 2219, 'game_mode': 3, 'deaths': 7, 'hero_id': 4, 'start_time': 1603611729, 'match_id': 5671181448, 'skill': 2, 'party_size': 4, 'lobby_type': 0, 'player_slot': 0}, {'kills': 7, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 10, 'duration': 2069, 'game_mode': 3, 'deaths': 3, 'hero_id': 35, 'start_time': 1603609106, 'match_id': 5671132518, 'skill': 3, 'party_size': 3, 'lobby_type': 0, 'player_slot': 128}, {'kills': 7, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 16, 'duration': 2549, 'game_mode': 3, 'deaths': 6, 'hero_id': 80, 'start_time': 1603606226, 'match_id': 5671083310, 'skill': 3, 'party_size': 3, 'lobby_type': 0, 'player_slot': 129}, {'kills': 3, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 5, 'duration': 1957, 'game_mode': 22, 'deaths': 8, 'hero_id': 18, 'start_time': 1603603893, 'match_id': 5671045176, 'skill': 3, 'party_size': 3, 'lobby_type': 0, 'player_slot': 129}, {'kills': 9, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 12, 'duration': 2157, 'game_mode': 22, 'deaths': 10, 'hero_id': 67, 'start_time': 1603557507, 'match_id': 5670366377, 'skill': 2, 'party_size': 2, 'lobby_type': 7, 'player_slot': 128}, {'kills': 6, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 10, 'duration': 1993, 'game_mode': 3, 'deaths': 4, 'hero_id': 18, 'start_time': 1603457167, 'match_id': 5668508119, 'skill': 2, 'party_size': 3, 'lobby_type': 0, 'player_slot': 2}, {'kills': 22, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 17, 'duration': 3312, 'game_mode': 22, 'deaths': 7, 'hero_id': 1, 'start_time': 1603453536, 'match_id': 5668429796, 'skill': None, 'party_size': 3, 'lobby_type': 0, 'player_slot': 128}, {'kills': 5, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 13, 'duration': 2443, 'game_mode': 3, 'deaths': 5, 'hero_id': 17, 'start_time': 1603450807, 'match_id': 5668379038, 'skill': 1, 'party_size': 2, 'lobby_type': 0, 'player_slot': 130}, {'kills': 0, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 9, 'duration': 2066, 'game_mode': 22, 'deaths': 5, 'hero_id': 67, 'start_time': 1603372754, 'match_id': 5667244405, 'skill': 2, 'party_size': 3, 'lobby_type': 0, 'player_slot': 1}, {'kills': 7, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 14, 'duration': 2242, 'game_mode': 22, 'deaths': 6, 'hero_id': 15, 'start_time': 1603370216, 'match_id': 5667185677, 'skill': 2, 'party_size': 3, 'lobby_type': 0, 'player_slot': 130}, {'kills': 9, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 16, 'duration': 2492, 'game_mode': 3, 'deaths': 3, 'hero_id': 67, 'start_time': 1603287623, 'match_id': 5665997247, 'skill': 2, 'party_size': 4, 'lobby_type': 0, 'player_slot': 129}, {'kills': 5, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 5, 'duration': 2203, 'game_mode': 22, 'deaths': 7, 'hero_id': 35, 'start_time': 1603285019, 'match_id': 5665934233, 'skill': 2, 'party_size': 3, 'lobby_type': 0, 'player_slot': 129}, {'kills': 7, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 6, 'duration': 2365, 'game_mode': 3, 'deaths': 8, 'hero_id': 8, 'start_time': 1603282200, 'match_id': 5665871925, 'skill': 2, 'party_size': 3, 'lobby_type': 0, 'player_slot': 1}, {'kills': 20, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 16, 'duration': 2227, 'game_mode': 3, 'deaths': 6, 'hero_id': 18, 'start_time': 1603279511, 'match_id': 5665819348, 'skill': 2, 'party_size': 2, 'lobby_type': 0, 'player_slot': 130}, {'kills': 6, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 6, 'duration': 2165, 'game_mode': 3, 'deaths': 8, 'hero_id': 95, 'start_time': 1603200635, 'match_id': 5664716019, 'skill': 3, 'party_size': 3, 'lobby_type': 0, 'player_slot': 2}, {'kills': 2, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 1, 'duration': 1611, 'game_mode': 3, 'deaths': 7, 'hero_id': 29, 'start_time': 1603198550, 'match_id': 5664666121, 'skill': 3, 'party_size': 4, 'lobby_type': 0, 'player_slot': 129}, {'kills': 6, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 18, 'duration': 4008, 'game_mode': 3, 'deaths': 13, 'hero_id': 51, 'start_time': 1603193697, 'match_id': 5664564743, 'skill': 2, 'party_size': 4, 'lobby_type': 0, 'player_slot': 128}, {'kills': 10, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 13, 'duration': 3050, 'game_mode': 22, 'deaths': 3, 'hero_id': 1, 'start_time': 1603189742, 'match_id': 5664497236, 'skill': 3, 'party_size': 3, 'lobby_type': 0, 'player_slot': 129}, {'kills': 9, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 11, 'duration': 2853, 'game_mode': 3, 'deaths': 8, 'hero_id': 35, 'start_time': 1603186396, 'match_id': 5664447496, 'skill': 1, 'party_size': 2, 'lobby_type': 0, 'player_slot': 128}, {'kills': 8, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 6, 'duration': 2130, 'game_mode': 22, 'deaths': 4, 'hero_id': 18, 'start_time': 1603112839, 'match_id': 5663403386, 'skill': 2, 'party_size': 4, 'lobby_type': 0, 'player_slot': 131}, {'kills': 9, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 15, 'duration': 2228, 'game_mode': 22, 'deaths': 7, 'hero_id': 30, 'start_time': 1603110290, 'match_id': 5663344042, 'skill': 2, 'party_size': 4, 'lobby_type': 0, 'player_slot': 4}], 135885299: [{'kills': 14, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 15, 'duration': 2108, 'game_mode': 22, 'deaths': 3, 'hero_id': 25, 'start_time': 1603635616, 'match_id': 5671723688, 'skill': 3, 'party_size': 3, 'lobby_type': 0, 'player_slot': 130}, {'kills': 7, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 6, 'duration': 2488, 'game_mode': 3, 'deaths': 10, 'hero_id': 47, 'start_time': 1603632522, 'match_id': 5671638162, 'skill': 2, 'party_size': 3, 'lobby_type': 0, 'player_slot': 128}, {'kills': 7, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 17, 'duration': 2890, 'game_mode': 3, 'deaths': 12, 'hero_id': 2, 'start_time': 1603623265, 'match_id': 5671412804, 'skill': 2, 'party_size': 5, 'lobby_type': 0, 'player_slot': 129}, {'kills': 3, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 6, 'duration': 1736, 'game_mode': 3, 'deaths': 8, 'hero_id': 28, 'start_time': 1603621266, 'match_id': 5671371804, 'skill': 2, 'party_size': 5, 'lobby_type': 0, 'player_slot': 129}, {'kills': 2, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 9, 'duration': 2609, 'game_mode': 3, 'deaths': 11, 'hero_id': 129, 'start_time': 1603617321, 'match_id': 5671293405, 'skill': 3, 'party_size': 5, 'lobby_type': 0, 'player_slot': 1}, {'kills': 7, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 23, 'duration': 2689, 'game_mode': 3, 'deaths': 5, 'hero_id': 42, 'start_time': 1603614268, 'match_id': 5671231312, 'skill': 2, 'party_size': 5, 'lobby_type': 0, 'player_slot': 129}, {'kills': 4, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 21, 'duration': 2219, 'game_mode': 3, 'deaths': 5, 'hero_id': 108, 'start_time': 1603611729, 'match_id': 5671181448, 'skill': 2, 'party_size': 4, 'lobby_type': 0, 'player_slot': 1}, {'kills': 5, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 13, 'duration': 2069, 'game_mode': 3, 'deaths': 5, 'hero_id': 28, 'start_time': 1603609106, 'match_id': 5671132518, 'skill': 3, 'party_size': 3, 'lobby_type': 0, 'player_slot': 129}, {'kills': 5, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 21, 'duration': 2549, 'game_mode': 3, 'deaths': 9, 'hero_id': 14, 'start_time': 1603606226, 'match_id': 5671083310, 'skill': 3, 'party_size': 3, 'lobby_type': 0, 'player_slot': 130}, {'kills': 4, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 8, 'duration': 1957, 'game_mode': 22, 'deaths': 9, 'hero_id': 15, 'start_time': 1603603893, 'match_id': 5671045176, 'skill': 3, 'party_size': 3, 'lobby_type': 0, 'player_slot': 130}], 194765012: [{'kills': 3, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 20, 'duration': 2890, 'game_mode': 3, 'deaths': 12, 'hero_id': 71, 'start_time': 1603623265, 'match_id': 5671412804, 'skill': 2, 'party_size': 5, 'lobby_type': 0, 'player_slot': 132}, {'kills': 4, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 6, 'duration': 1736, 'game_mode': 3, 'deaths': 9, 'hero_id': 7, 'start_time': 1603621266, 'match_id': 5671371804, 'skill': 2, 'party_size': 5, 'lobby_type': 0, 'player_slot': 132}, {'kills': 1, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 12, 'duration': 2609, 'game_mode': 3, 'deaths': 11, 'hero_id': 106, 'start_time': 1603617321, 'match_id': 5671293405, 'skill': 3, 'party_size': 5, 'lobby_type': 0, 'player_slot': 4}, {'kills': 1, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 8, 'duration': 2689, 'game_mode': 3, 'deaths': 9, 'hero_id': 13, 'start_time': 1603614268, 'match_id': 5671231312, 'skill': 2, 'party_size': 5, 'lobby_type': 0, 'player_slot': 132}, {'kills': 5, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 28, 'duration': 3804, 'game_mode': 22, 'deaths': 8, 'hero_id': 110, 'start_time': 1603459769, 'match_id': 5668570685, 'skill': 2, 'party_size': 3, 'lobby_type': 0, 'player_slot': 130}, {'kills': 4, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 15, 'duration': 1993, 'game_mode': 3, 'deaths': 6, 'hero_id': 7, 'start_time': 1603457167, 'match_id': 5668508119, 'skill': 2, 'party_size': 3, 'lobby_type': 0, 'player_slot': 3}, {'kills': 5, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 19, 'duration': 3312, 'game_mode': 22, 'deaths': 17, 'hero_id': 88, 'start_time': 1603453536, 'match_id': 5668429796, 'skill': None, 'party_size': 3, 'lobby_type': 0, 'player_slot': 129}, {'kills': 3, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 11, 'duration': 2443, 'game_mode': 3, 'deaths': 8, 'hero_id': 19, 'start_time': 1603450807, 'match_id': 5668379038, 'skill': 1, 'party_size': 2, 'lobby_type': 0, 'player_slot': 131}, {'kills': 4, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 1, 'duration': 2066, 'game_mode': 22, 'deaths': 7, 'hero_id': 62, 'start_time': 1603372754, 'match_id': 5667244405, 'skill': 2, 'party_size': 3, 'lobby_type': 0, 'player_slot': 3}, {'kills': 4, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 20, 'duration': 2242, 'game_mode': 22, 'deaths': 4, 'hero_id': 88, 'start_time': 1603370216, 'match_id': 5667185677, 'skill': 2, 'party_size': 3, 'lobby_type': 0, 'player_slot': 132}, {'kills': 2, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 20, 'duration': 2492, 'game_mode': 3, 'deaths': 7, 'hero_id': 9, 'start_time': 1603287623, 'match_id': 5665997247, 'skill': 2, 'party_size': 4, 'lobby_type': 0, 'player_slot': 130}, {'kills': 3, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 13, 'duration': 2203, 'game_mode': 22, 'deaths': 8, 'hero_id': 90, 'start_time': 1603285019, 'match_id': 5665934233, 'skill': 2, 'party_size': 3, 'lobby_type': 0, 'player_slot': 130}, {'kills': 11, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 3, 'duration': 2365, 'game_mode': 3, 'deaths': 9, 'hero_id': 25, 'start_time': 1603282200, 'match_id': 5665871925, 'skill': 2, 'party_size': 3, 'lobby_type': 0, 'player_slot': 2}, {'kills': 1, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 3, 'duration': 1611, 'game_mode': 3, 'deaths': 9, 'hero_id': 7, 'start_time': 1603198550, 'match_id': 5664666121, 'skill': 3, 'party_size': 4, 'lobby_type': 0, 'player_slot': 130}, {'kills': 4, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 17, 'duration': 4008, 'game_mode': 3, 'deaths': 13, 'hero_id': 13, 'start_time': 1603193697, 'match_id': 5664564743, 'skill': 2, 'party_size': 4, 'lobby_type': 0, 'player_slot': 129}, {'kills': 4, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 17, 'duration': 3050, 'game_mode': 22, 'deaths': 5, 'hero_id': 45, 'start_time': 1603189742, 'match_id': 5664497236, 'skill': 3, 'party_size': 3, 'lobby_type': 0, 'player_slot': 130}, {'kills': 1, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 6, 'duration': 2853, 'game_mode': 3, 'deaths': 10, 'hero_id': 13, 'start_time': 1603186396, 'match_id': 5664447496, 'skill': 1, 'party_size': 2, 'lobby_type': 0, 'player_slot': 129}, {'kills': 8, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 20, 'duration': 2130, 'game_mode': 22, 'deaths': 8, 'hero_id': 9, 'start_time': 1603112839, 'match_id': 5663403386, 'skill': 2, 'party_size': 4, 'lobby_type': 0, 'player_slot': 130}, {'kills': 2, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 17, 'duration': 2228, 'game_mode': 22, 'deaths': 10, 'hero_id': 7, 'start_time': 1603110290, 'match_id': 5663344042, 'skill': 2, 'party_size': 4, 'lobby_type': 0, 'player_slot': 3}, {'kills': 3, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 6, 'duration': 2518, 'game_mode': 3, 'deaths': 8, 'hero_id': 83, 'start_time': 1603107012, 'match_id': 5663277198, 'skill': 3, 'party_size': 3, 'lobby_type': 0, 'player_slot': 2}, {'kills': 9, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 7, 'duration': 2801, 'game_mode': 22, 'deaths': 6, 'hero_id': 54, 'start_time': 1603099717, 'match_id': 5663160703, 'skill': 1, 'party_size': 1, 'lobby_type': 0, 'player_slot': 132}], 163338929: [], 142874459: [{'kills': 14, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 11, 'duration': 2890, 'game_mode': 3, 'deaths': 7, 'hero_id': 35, 'start_time': 1603623265, 'match_id': 5671412804, 'skill': 2, 'party_size': 5, 'lobby_type': 0, 'player_slot': 130}, {'kills': 5, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 8, 'duration': 1736, 'game_mode': 3, 'deaths': 10, 'hero_id': 15, 'start_time': 1603621266, 'match_id': 5671371804, 'skill': 2, 'party_size': 5, 'lobby_type': 0, 'player_slot': 130}, {'kills': 5, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 9, 'duration': 2609, 'game_mode': 3, 'deaths': 11, 'hero_id': 47, 'start_time': 1603617321, 'match_id': 5671293405, 'skill': 3, 'party_size': 5, 'lobby_type': 0, 'player_slot': 2}, {'kills': 10, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 8, 'duration': 2689, 'game_mode': 3, 'deaths': 7, 'hero_id': 44, 'start_time': 1603614268, 'match_id': 5671231312, 'skill': 2, 'party_size': 5, 'lobby_type': 0, 'player_slot': 130}, {'kills': 11, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 13, 'duration': 2219, 'game_mode': 3, 'deaths': 3, 'hero_id': 35, 'start_time': 1603611729, 'match_id': 5671181448, 'skill': 2, 'party_size': 4, 'lobby_type': 0, 'player_slot': 2}, {'kills': 1, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 24, 'duration': 3804, 'game_mode': 22, 'deaths': 6, 'hero_id': 29, 'start_time': 1603459769, 'match_id': 5668570685, 'skill': 2, 'party_size': 3, 'lobby_type': 0, 'player_slot': 129}, {'kills': 9, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 13, 'duration': 1993, 'game_mode': 3, 'deaths': 5, 'hero_id': 15, 'start_time': 1603457167, 'match_id': 5668508119, 'skill': 2, 'party_size': 3, 'lobby_type': 0, 'player_slot': 4}, {'kills': 8, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 29, 'duration': 3312, 'game_mode': 22, 'deaths': 13, 'hero_id': 108, 'start_time': 1603453536, 'match_id': 5668429796, 'skill': None, 'party_size': 3, 'lobby_type': 0, 'player_slot': 130}, {'kills': 10, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 10, 'duration': 1984, 'game_mode': 22, 'deaths': 4, 'hero_id': 2, 'start_time': 1603375483, 'match_id': 5667313190, 'skill': 1, 'party_size': 1, 'lobby_type': 0, 'player_slot': 130}, {'kills': 3, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 22, 'duration': 2492, 'game_mode': 3, 'deaths': 4, 'hero_id': 108, 'start_time': 1603287623, 'match_id': 5665997247, 'skill': 2, 'party_size': 4, 'lobby_type': 0, 'player_slot': 128}, {'kills': 1, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 17, 'duration': 2203, 'game_mode': 22, 'deaths': 9, 'hero_id': 108, 'start_time': 1603285019, 'match_id': 5665934233, 'skill': 2, 'party_size': 3, 'lobby_type': 0, 'player_slot': 128}, {'kills': 3, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 14, 'duration': 2365, 'game_mode': 3, 'deaths': 15, 'hero_id': 31, 'start_time': 1603282200, 'match_id': 5665871925, 'skill': 2, 'party_size': 3, 'lobby_type': 0, 'player_slot': 0}, {'kills': 5, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 29, 'duration': 2227, 'game_mode': 3, 'deaths': 9, 'hero_id': 5, 'start_time': 1603279511, 'match_id': 5665819348, 'skill': 2, 'party_size': 2, 'lobby_type': 0, 'player_slot': 129}, {'kills': 6, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 16, 'duration': 2130, 'game_mode': 22, 'deaths': 5, 'hero_id': 5, 'start_time': 1603112839, 'match_id': 5663403386, 'skill': 2, 'party_size': 4, 'lobby_type': 0, 'player_slot': 129}, {'kills': 3, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 24, 'duration': 2228, 'game_mode': 22, 'deaths': 2, 'hero_id': 108, 'start_time': 1603110290, 'match_id': 5663344042, 'skill': 2, 'party_size': 4, 'lobby_type': 0, 'player_slot': 2}, {'kills': 2, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 9, 'duration': 2518, 'game_mode': 3, 'deaths': 4, 'hero_id': 45, 'start_time': 1603107012, 'match_id': 5663277198, 'skill': 3, 'party_size': 3, 'lobby_type': 0, 'player_slot': 1}], 163287641: [{'kills': 18, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 13, 'duration': 2463, 'game_mode': 22, 'deaths': 6, 'hero_id': 28, 'start_time': 1603207905, 'match_id': 5664894454, 'skill': 2, 'party_size': 2, 'lobby_type': 7, 'player_slot': 3}, {'kills': 9, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 6, 'duration': 1430, 'game_mode': 22, 'deaths': 0, 'hero_id': 97, 'start_time': 1603205680, 'match_id': 5664842367, 'skill': 2, 'party_size': 2, 'lobby_type': 7, 'player_slot': 2}, {'kills': 11, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 5, 'duration': 2165, 'game_mode': 3, 'deaths': 11, 'hero_id': 101, 'start_time': 1603200635, 'match_id': 5664716019, 'skill': 3, 'party_size': 3, 'lobby_type': 0, 'player_slot': 4}, {'kills': 0, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 1, 'duration': 1611, 'game_mode': 3, 'deaths': 6, 'hero_id': 126, 'start_time': 1603198550, 'match_id': 5664666121, 'skill': 3, 'party_size': 4, 'lobby_type': 0, 'player_slot': 131}, {'kills': 18, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 11, 'duration': 4008, 'game_mode': 3, 'deaths': 11, 'hero_id': 21, 'start_time': 1603193697, 'match_id': 5664564743, 'skill': 2, 'party_size': 4, 'lobby_type': 0, 'player_slot': 130}, {'kills': 12, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 12, 'duration': 3050, 'game_mode': 22, 'deaths': 7, 'hero_id': 28, 'start_time': 1603189742, 'match_id': 5664497236, 'skill': 3, 'party_size': 3, 'lobby_type': 0, 'player_slot': 131}, {'kills': 14, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 15, 'duration': 2361, 'game_mode': 22, 'deaths': 4, 'hero_id': 21, 'start_time': 1603120478, 'match_id': 5663594060, 'skill': 2, 'party_size': 2, 'lobby_type': 7, 'player_slot': 128}, {'kills': 14, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 11, 'duration': 2130, 'game_mode': 22, 'deaths': 5, 'hero_id': 97, 'start_time': 1603112839, 'match_id': 5663403386, 'skill': 2, 'party_size': 4, 'lobby_type': 0, 'player_slot': 128}, {'kills': 13, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 6, 'duration': 2228, 'game_mode': 22, 'deaths': 5, 'hero_id': 28, 'start_time': 1603110290, 'match_id': 5663344042, 'skill': 2, 'party_size': 4, 'lobby_type': 0, 'player_slot': 1}, {'kills': 11, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 5, 'duration': 2518, 'game_mode': 3, 'deaths': 8, 'hero_id': 21, 'start_time': 1603107012, 'match_id': 5663277198, 'skill': 3, 'party_size': 3, 'lobby_type': 0, 'player_slot': 0}], 144128282: [{'kills': 9, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 15, 'duration': 2689, 'game_mode': 3, 'deaths': 14, 'hero_id': 62, 'start_time': 1603614268, 'match_id': 5671231312, 'skill': 2, 'party_size': 5, 'lobby_type': 0, 'player_slot': 131}, {'kills': 4, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 23, 'duration': 2219, 'game_mode': 3, 'deaths': 6, 'hero_id': 30, 'start_time': 1603611729, 'match_id': 5671181448, 'skill': 2, 'party_size': 4, 'lobby_type': 0, 'player_slot': 3}, {'kills': 7, 'radiant_win': False, 'version': None, 'leaver_status': 1, 'assists': 9, 'duration': 2069, 'game_mode': 3, 'deaths': 7, 'hero_id': 22, 'start_time': 1603609106, 'match_id': 5671132518, 'skill': 3, 'party_size': 3, 'lobby_type': 0, 'player_slot': 130}, {'kills': 3, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 20, 'duration': 2549, 'game_mode': 3, 'deaths': 10, 'hero_id': 5, 'start_time': 1603606226, 'match_id': 5671083310, 'skill': 3, 'party_size': 3, 'lobby_type': 0, 'player_slot': 131}, {'kills': 5, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 7, 'duration': 1957, 'game_mode': 22, 'deaths': 9, 'hero_id': 58, 'start_time': 1603603893, 'match_id': 5671045176, 'skill': 3, 'party_size': 3, 'lobby_type': 0, 'player_slot': 131}, {'kills': 3, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 15, 'duration': 2157, 'game_mode': 22, 'deaths': 17, 'hero_id': 84, 'start_time': 1603557507, 'match_id': 5670366377, 'skill': 2, 'party_size': 2, 'lobby_type': 7, 'player_slot': 129}, {'kills': 3, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 5, 'duration': 1651, 'game_mode': 3, 'deaths': 6, 'hero_id': 99, 'start_time': 1603550716, 'match_id': 5670188565, 'skill': 1, 'party_size': 3, 'lobby_type': 0, 'player_slot': 3}, {'kills': 7, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 13, 'duration': 3477, 'game_mode': 3, 'deaths': 14, 'hero_id': 119, 'start_time': 1603546871, 'match_id': 5670081324, 'skill': None, 'party_size': 4, 'lobby_type': 0, 'player_slot': 2}], 189119223: [{'kills': 21, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 14, 'duration': 2216, 'game_mode': 3, 'deaths': 2, 'hero_id': 44, 'start_time': 1603630468, 'match_id': 5671582696, 'skill': 2, 'party_size': 3, 'lobby_type': 7, 'player_slot': 2}, {'kills': 9, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 7, 'duration': 2454, 'game_mode': 22, 'deaths': 8, 'hero_id': 48, 'start_time': 1603627736, 'match_id': 5671513277, 'skill': 2, 'party_size': 3, 'lobby_type': 7, 'player_slot': 2}, {'kills': 3, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 6, 'duration': 1549, 'game_mode': 3, 'deaths': 9, 'hero_id': 56, 'start_time': 1603625918, 'match_id': 5671470430, 'skill': 1, 'party_size': 3, 'lobby_type': 7, 'player_slot': 0}, {'kills': 16, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 18, 'duration': 2482, 'game_mode': 3, 'deaths': 4, 'hero_id': 39, 'start_time': 1603547392, 'match_id': 5670096098, 'skill': 1, 'party_size': 4, 'lobby_type': 0, 'player_slot': 1}, {'kills': 25, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 16, 'duration': 2948, 'game_mode': 3, 'deaths': 4, 'hero_id': 63, 'start_time': 1603544172, 'match_id': 5670009397, 'skill': None, 'party_size': 4, 'lobby_type': 0, 'player_slot': 1}, {'kills': 3, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 3, 'duration': 2038, 'game_mode': 3, 'deaths': 11, 'hero_id': 99, 'start_time': 1603541788, 'match_id': 5669950547, 'skill': 1, 'party_size': 4, 'lobby_type': 0, 'player_slot': 129}, {'kills': 12, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 23, 'duration': 2562, 'game_mode': 22, 'deaths': 2, 'hero_id': 56, 'start_time': 1603526613, 'match_id': 5669652165, 'skill': 2, 'party_size': 1, 'lobby_type': 7, 'player_slot': 3}, {'kills': 2, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 5, 'duration': 1903, 'game_mode': 3, 'deaths': 5, 'hero_id': 44, 'start_time': 1603524299, 'match_id': 5669611175, 'skill': 2, 'party_size': 1, 'lobby_type': 7, 'player_slot': 130}, {'kills': 7, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 10, 'duration': 2310, 'game_mode': 22, 'deaths': 4, 'hero_id': 8, 'start_time': 1603521250, 'match_id': 5669560868, 'skill': 3, 'party_size': 1, 'lobby_type': 7, 'player_slot': 130}, {'kills': 21, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 16, 'duration': 4030, 'game_mode': 3, 'deaths': 8, 'hero_id': 44, 'start_time': 1603506945, 'match_id': 5669360433, 'skill': 3, 'party_size': 1, 'lobby_type': 7, 'player_slot': 1}, {'kills': 2, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 8, 'duration': 2416, 'game_mode': 22, 'deaths': 7, 'hero_id': 84, 'start_time': 1603504107, 'match_id': 5669327200, 'skill': 3, 'party_size': 1, 'lobby_type': 7, 'player_slot': 131}, {'kills': 18, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 12, 'duration': 3804, 'game_mode': 22, 'deaths': 6, 'hero_id': 39, 'start_time': 1603459769, 'match_id': 5668570685, 'skill': 2, 'party_size': 3, 'lobby_type': 0, 'player_slot': 131}, {'kills': 4, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 7, 'duration': 2066, 'game_mode': 22, 'deaths': 9, 'hero_id': 40, 'start_time': 1603372754, 'match_id': 5667244405, 'skill': 2, 'party_size': 3, 'lobby_type': 0, 'player_slot': 2}, {'kills': 1, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 17, 'duration': 2242, 'game_mode': 22, 'deaths': 5, 'hero_id': 84, 'start_time': 1603370216, 'match_id': 5667185677, 'skill': 2, 'party_size': 3, 'lobby_type': 0, 'player_slot': 131}, {'kills': 11, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 14, 'duration': 2492, 'game_mode': 3, 'deaths': 3, 'hero_id': 39, 'start_time': 1603287623, 'match_id': 5665997247, 'skill': 2, 'party_size': 4, 'lobby_type': 0, 'player_slot': 131}, {'kills': 7, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 14, 'duration': 1767, 'game_mode': 3, 'deaths': 1, 'hero_id': 63, 'start_time': 1603242570, 'match_id': 5665372140, 'skill': 2, 'party_size': 1, 'lobby_type': 7, 'player_slot': 130}, {'kills': 4, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 11, 'duration': 2165, 'game_mode': 3, 'deaths': 10, 'hero_id': 14, 'start_time': 1603200635, 'match_id': 5664716019, 'skill': 3, 'party_size': 3, 'lobby_type': 0, 'player_slot': 3}, {'kills': 2, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 1, 'duration': 1611, 'game_mode': 3, 'deaths': 8, 'hero_id': 83, 'start_time': 1603198550, 'match_id': 5664666121, 'skill': 3, 'party_size': 4, 'lobby_type': 0, 'player_slot': 132}], 307998042: [{'kills': 3, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 9, 'duration': 2488, 'game_mode': 3, 'deaths': 10, 'hero_id': 101, 'start_time': 1603632522, 'match_id': 5671638162, 'skill': 2, 'party_size': 3, 'lobby_type': 0, 'player_slot': 130}, {'kills': 4, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 6, 'duration': 1896, 'game_mode': 22, 'deaths': 1, 'hero_id': 94, 'start_time': 1603629998, 'match_id': 5671569914, 'skill': 1, 'party_size': 1, 'lobby_type': 7, 'player_slot': 131}, {'kills': 23, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 11, 'duration': 3541, 'game_mode': 22, 'deaths': 7, 'hero_id': 35, 'start_time': 1603274519, 'match_id': 5665738711, 'skill': 1, 'party_size': 1, 'lobby_type': 7, 'player_slot': 128}, {'kills': 2, 'radiant_win': True, 'version': None, 'leaver_status': 0, 'assists': 23, 'duration': 4008, 'game_mode': 3, 'deaths': 13, 'hero_id': 75, 'start_time': 1603193697, 'match_id': 5664564743, 'skill': 2, 'party_size': 4, 'lobby_type': 0, 'player_slot': 131}], 137479998: [{'kills': 10, 'radiant_win': False, 'version': None, 'leaver_status': 0, 'assists': 27, 'duration': 2108, 'game_mode': 22, 'deaths': 5, 'hero_id': 16, 'start_time': 1603635616, 'match_id': 5671723688, 'skill': 3, 'party_size': 3, 'lobby_type': 0, 'player_slot': 132}]}
    duration_conclusion = get_weekly_duration_conclusion(data)
    print(str(duration_conclusion))
    wl_conclusion = get_weekly_wl_conclusion()
    print(str(wl_conclusion))
    kill_conclusion = get_weekly_kill_conclusion(data)
    print(str(kill_conclusion))
    death_conclusion = get_weekly_death_conclusion(data)
    print(str(death_conclusion))
    assist_conclusion = get_weekly_assistant_conclusion(data)
    print(str(assist_conclusion))

def send_all_weekly_conclusion():
    data = get_all_player_latest_days_match(7)
    duration_conclusion = get_weekly_duration_conclusion(data)
    try:
        sender.send(str(duration_conclusion))
    except:
        pass
    wl_conclusion = get_weekly_wl_conclusion()
    try:
        sender.send(str(wl_conclusion))
    except:
        pass
    kill_conclusion = get_weekly_kill_conclusion(data)
    try:
        sender.send(str(kill_conclusion))
    except:
        pass
    death_conclusion = get_weekly_death_conclusion(data)
    try:
        sender.send(str(death_conclusion))
    except:
        pass
    assist_conclusion = get_weekly_assistant_conclusion(data)
    try:
        sender.send(str(assist_conclusion))
    except:
        pass

def get_weekly_duration_conclusion(data):
    res = {}
    conclusion = "本周天道酬勤榜（加速模式不算）==========================="
    for k,v in data.items():
        t = 0
        try:
            for m in v:
                t = t + m['duration']
            res[k] = t
        except:
            pass
    res = sorted(res.items(),reverse=True, key = lambda kv:(kv[1], kv[0]))
    i = 1
    for k,v in res:
        conclusion = conclusion + "第" + str(i) + "名:" + get_player_name_by_id(k) + "," + str(datetime.timedelta(seconds=v)) + "。"
        i = i + 1
    return conclusion

def get_weekly_kill_conclusion(data):
    res = {}
    conclusion = "本周场均击杀榜（加速模式不算，少于5场不算）=================="
    top1_player = 0
    for k,v in data.items():
        t = 0
        j = 0
        try:
            for m in v:
                t = t + m['kills']
                j = j + 1
        except:
            pass
        if j >= 5:
            res[k] = float('%.3f' % (t / j))
    res = sorted(res.items(),reverse=True, key = lambda kv:(kv[1], kv[0]))
    i = 1
    for k,v in res:
        conclusion = conclusion + "第" + str(i) + "名:" + get_player_name_by_id(k) + "," + str(v) + "。"
        if i == 1:
            top1_player = k
        i = i + 1
    return conclusion

def get_weekly_death_conclusion(data):
    res = {}
    conclusion = "本周场均死亡榜（加速模式不算，少于5场不算）=================="
    top1_player = 0
    for k,v in data.items():
        t = 0
        j = 0
        try:
            for m in v:
                t = t + m['deaths']
                j = j + 1
        except:
            pass
        if j >= 5:
            res[k] = float('%.3f' % (t / j))
    res = sorted(res.items(),reverse=True, key = lambda kv:(kv[1], kv[0]))
    i = 1
    for k,v in res:
        conclusion = conclusion + "第" + str(i) + "名:" + get_player_name_by_id(k) + "," + str(v) + "。"
        if i == 1:
            top1_player = k
        i = i + 1
    conclusion = conclusion + "恭喜" + get_player_name_by_id(top1_player) + "获得了本周送头王的称号。"
    return conclusion

def get_weekly_assistant_conclusion(data):
    res = {}
    conclusion = "本周场均助攻榜（加速模式不算，少于5场不算）=================="
    top1_player = 0
    for k,v in data.items():
        t = 0
        j = 0
        try:
            for m in v:
                t = t + m['assists']
                j = j + 1
        except:
            pass
        if j >= 5:
            res[k] = float('%.3f' % (t / j))
    res = sorted(res.items(),reverse=True, key = lambda kv:(kv[1], kv[0]))
    i = 1
    for k,v in res:
        conclusion = conclusion + "第" + str(i) + "名:" + get_player_name_by_id(k) + "," + str(v) + "。"
        if i == 1:
            top1_player = k
        i = i + 1
    conclusion = conclusion + "U1S1," + get_player_name_by_id(top1_player) + "也是个老辅助了。"
    return conclusion

def getWL(id, date):
    rsp = requests.get("https://api.opendota.com/api/players/" + str(id) + "/wl?api_key=" + key + "&date=" + str(date))
    if rsp.status_code == 200:
        rspJson = json.loads(rsp.text)
        return rspJson
    else:
        return -1

def get_all_player_latest_days_wl(date):
    s = requests.Session()
    data = {}
    for p in players.keys():
        rsp = s.get("https://api.opendota.com/api/players/" + str(p) + "/wl?api_key=" + key + "&date=" + str(date))
        if rsp.status_code == 200:
            rspJson = json.loads(rsp.text)
            data[p] = rspJson
        else:
            print("error")
    return data

def get_weekly_wl_conclusion():
    data = get_all_player_latest_days_wl(7)
    conclusion = "本周胜率榜（至少5场才算）==========================="
    res = {}
    for k,v in data.items():
        if v['win'] + v['lose'] >= 5:
            rate = v['win']/(v['win'] + v['lose'])
            rate = float('%.3f' % rate)
            res[k] = rate
    i = 1
    res = sorted(res.items(),reverse=True, key = lambda kv:(kv[1], kv[0]))
    for k,v in res:
        conclusion = conclusion + "第" + str(i) + "名:" + get_player_name_by_id(k) + ",胜率" + str(v) + "," + str(data[k]['win']) + "胜" + str(data[k]['lose']) + "负。"
        i = i + 1
    return conclusion

with open("./players_latest_match_ids.json",'r') as load_f:
    players_latest_match_ids = json.load(load_f)
scan_time = 0
while True:
    scan_time = scan_time + 1
    print("scanning " + str(scan_time))
    for p in players.keys():
        try:
            res, data = get_player_latest_game_conclusion(p)
            if data['match_id'] != players_latest_match_ids[str(p)]:
                players_latest_match_ids[str(p)] = data['match_id']
                sender.send(res)
                print("sending" + str(p))
            # if int(time.time()) - data['endtime'] <= refresh_sencond:
            #     print("sending" + str(p))
            #     send_player_latest_game_data(p)
        except:
            pass
    with open("./players_latest_match_ids.json", "w") as dump_f:
        json.dump(players_latest_match_ids, dump_f)
    time.sleep(refresh_sencond)

embed()
#sender.send(match)

