import time
import random
import sys
import subprocess
import json
import os
import inspect
import logging

# 配置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def install_missing_packages():
    required_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            print(f"缺少 {package}，正在安裝...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_missing_packages()

class Weapon:
    def __init__(self, name, min_attack, max_attack, required_realm, spirit=None, upgraded=False, enhancements=0):
        self.name = name
        self.base_min_attack = min_attack
        self.base_max_attack = max_attack
        self.required_realm = required_realm
        self.spirit = spirit
        self.upgraded = upgraded
        self.enhancements = enhancements
        self.update_stats()
        logging.info(f"初始化武器: {self.name}, 攻擊力: {self.min_attack}-{self.max_attack}")

    def update_stats(self):
        enhanced_min = self.base_min_attack + (self.enhancements * 5)
        enhanced_max = self.base_max_attack + (self.enhancements * 5)
        if self.spirit:
            factor = 1.3 if self.upgraded else 1.2
            self.min_attack = int(enhanced_min * factor)
            self.max_attack = int(enhanced_max * factor)
        else:
            self.min_attack = enhanced_min
            self.max_attack = enhanced_max

    def get_attack(self):
        return random.randint(self.min_attack, self.max_attack)

class Armor:
    def __init__(self, name, defense, required_realm):
        self.name = name
        self.defense = defense
        self.required_realm = required_realm
        logging.info(f"初始化防具: {self.name}, 防禦力: {self.defense}")

class Skill:
    def __init__(self, name, damage_factor, cooldown, required_realm, effect=None):
        self.name = name
        self.damage_factor = damage_factor
        self.cooldown = cooldown
        self.required_realm = required_realm
        self.effect = effect
        self.current_cooldown = 0
        logging.info(f"初始化技能: {self.name}, 傷害倍率: {self.damage_factor}")

    def apply(self, player, enemy_hp):
        if self.current_cooldown > 0:
            print(f"{self.name} 冷卻中 ({self.current_cooldown} 回合)")
            return enemy_hp, False
        
        if self.effect and self.name == "魔氣侵蝕" and player.spirit_stones < 10:
            print("靈石不足，無法使用魔氣侵蝕")
            return enemy_hp, False
        
        damage = int(player.get_total_attack() * self.damage_factor)
        if self.effect:
            self.effect(player)
        self.current_cooldown = self.cooldown
        print(f"釋放 {self.name}，造成 {damage} 傷害")
        return enemy_hp - damage, True

    def update_cooldown(self):
        if self.current_cooldown > 0:
            self.current_cooldown -= 1

class Spirit:
    def __init__(self, name):
        self.name = name
        logging.info(f"初始化器靈: {self.name}")

class Sect:
    def __init__(self, name, effect, allowed_path, allowed_specialty=None):
        self.name = name
        self.effect = effect
        self.allowed_path = allowed_path
        self.allowed_specialty = allowed_specialty
        logging.info(f"初始化宗門: {self.name}")

class Player:
    realms_xian = ["煉氣", "築基", "金丹", "元嬰", "化神", "大乘", "渡劫", "飛升"]
    realms_mo = ["魔徒", "凝煞", "魔丹", "化魔", "魔魂", "魔尊", "魔劫", "魔帝"]
    
    weapon_list_xian = {
        "jian": [Weapon("木劍", 5, 10, 0), Weapon("青銅劍", 10, 20, 1), Weapon("玄鐵劍", 20, 40, 2),
                 Weapon("靈劍·青鋒", 40, 80, 3), Weapon("仙劍·赤霄", 80, 160, 4), Weapon("誅仙劍", 160, 320, 5),
                 Weapon("軒轅劍", 320, 640, 6), Weapon("混沌劍", 640, 1280, 7)],
        "qiang": [Weapon("竹槍", 4, 12, 0), Weapon("鐵槍", 8, 24, 1), Weapon("銀槍", 16, 48, 2),
                  Weapon("靈槍·破空", 32, 96, 3), Weapon("仙槍·龍吟", 64, 192, 4), Weapon("天罰槍", 128, 384, 5),
                  Weapon("混元槍", 256, 768, 6), Weapon("星辰槍", 512, 1536, 7)],
        "dan": [Weapon("藥杵", 3, 8, 0), Weapon("銅鼎", 6, 16, 1), Weapon("煉丹爐", 12, 32, 2),
                Weapon("靈鼎·聚元", 24, 64, 3), Weapon("仙鼎·化虛", 48, 128, 4), Weapon("天丹鼎", 96, 256, 5),
                Weapon("混沌鼎", 192, 512, 6), Weapon("造化鼎", 384, 1024, 7)],
        "fa": [Weapon("符筆", 6, 9, 0), Weapon("靈符", 12, 18, 1), Weapon("法印", 24, 36, 2),
               Weapon("靈器·天璽", 48, 72, 3), Weapon("法寶·玄光", 96, 144, 4), Weapon("仙器·星盤", 192, 288, 5),
               Weapon("神器·天書", 384, 576, 6), Weapon("混沌法輪", 768, 1152, 7)]
    }
    armor_list_xian = {
        "jian": [Armor("布衣", 5, 0), Armor("皮甲", 10, 1), Armor("鐵甲", 20, 2), Armor("靈甲·青鱗", 40, 3),
                 Armor("法袍·紫霞", 80, 4), Armor("仙衣·霓裳", 160, 5), Armor("神鎧·不滅", 320, 6), Armor("混沌聖衣", 640, 7)],
        "qiang": [Armor("輕甲", 6, 0), Armor("鎖甲", 12, 1), Armor("重甲", 24, 2), Armor("靈甲·龍鱗", 48, 3),
                  Armor("仙鎧·金剛", 96, 4), Armor("天護甲", 192, 5), Armor("混元鎧", 384, 6), Armor("星辰甲", 768, 7)],
        "dan": [Armor("草袍", 4, 0), Armor("藥衣", 8, 1), Armor("丹袍", 16, 2), Armor("靈袍·養元", 32, 3),
                Armor("仙袍·生機", 64, 4), Armor("天丹衣", 128, 5), Armor("混沌藥袍", 256, 6), Armor("造化袍", 512, 7)],
        "fa": [Armor("道袍", 5, 0), Armor("符衣", 10, 1), Armor("法袍", 20, 2), Armor("靈袍·玄機", 40, 3),
               Armor("仙衣·星輝", 80, 4), Armor("天法袍", 160, 5), Armor("混沌法衣", 320, 6), Armor("聖法袍", 640, 7)]
    }
    weapon_list_mo = {
        "xue": [Weapon("骨刃", 6, 12, 0), Weapon("血刺", 12, 24, 1), Weapon("血爪", 24, 48, 2),
                Weapon("魔器·噬血", 48, 96, 3), Weapon("血刃·殞地", 96, 192, 4), Weapon("嗜血魔刀", 192, 384, 5),
                Weapon("魔皇血矛", 384, 768, 6), Weapon("混沌血源", 768, 1536, 7)],
        "hun": [Weapon("魂針", 5, 13, 0), Weapon("鬼爪", 10, 26, 1), Weapon("魂鏈", 20, 52, 2),
                Weapon("魔器·拘魂", 40, 104, 3), Weapon("魂刃·殞魂", 80, 208, 4), Weapon("噬魂魔鐮", 160, 416, 5),
                Weapon("魔皇魂鞭", 320, 832, 6), Weapon("混沌魂器", 640, 1664, 7)],
        "du": [Weapon("毒針", 4, 10, 0), Weapon("毒刃", 8, 20, 1), Weapon("毒爪", 16, 40, 2),
               Weapon("魔器·腐毒", 32, 80, 3), Weapon("毒刃·殞命", 64, 160, 4), Weapon("噬毒魔針", 128, 320, 5),
               Weapon("魔皇毒矛", 256, 640, 6), Weapon("混沌毒源", 512, 1280, 7)],
        "moyan": [Weapon("焰刺", 7, 11, 0), Weapon("魔焰刀", 14, 22, 1), Weapon("焰爪", 28, 44, 2),
                  Weapon("魔器·焚魂", 56, 88, 3), Weapon("焰刃·殞天", 112, 176, 4), Weapon("魔焰霸刀", 224, 352, 5),
                  Weapon("魔皇焰戟", 448, 704, 6), Weapon("混沌焰源", 896, 1408, 7)]
    }
    armor_list_mo = {
        "xue": [Armor("殘袍", 6, 0), Armor("骨甲", 12, 1), Armor("血鎧", 24, 2), Armor("魔魂甲", 48, 3),
                Armor("噬血袍", 96, 4), Armor("血魔戰衣", 192, 5), Armor("魔皇血殼", 384, 6), Armor("混沌血甲", 768, 7)],
        "hun": [Armor("魂衣", 5, 0), Armor("鬼袍", 10, 1), Armor("魂甲", 20, 2), Armor("魔魂袍", 40, 3),
                Armor("噬魂衣", 80, 4), Armor("魂魔戰袍", 160, 5), Armor("魔皇魂殼", 320, 6), Armor("混沌魂甲", 640, 7)],
        "du": [Armor("毒布", 4, 0), Armor("毒皮", 8, 1), Armor("毒甲", 16, 2), Armor("魔毒袍", 32, 3),
               Armor("噬毒衣", 64, 4), Armor("毒魔戰衣", 128, 5), Armor("魔皇毒殼", 256, 6), Armor("混沌毒甲", 512, 7)],
        "moyan": [Armor("焰袍", 7, 0), Armor("焰甲", 14, 1), Armor("魔焰鎧", 28, 2), Armor("魔焰戰袍", 56, 3),
                  Armor("噬焰衣", 112, 4), Armor("焰魔戰衣", 224, 5), Armor("魔皇焰殼", 448, 6), Armor("混沌焰甲", 896, 7)]
    }
    
    skill_list_xian = {
        "jian": [Skill("劍氣斬", 1.5, 2, 1), Skill("劍影分光", 1.8, 3, 2), Skill("劍氣縱橫", 1.6, 3, 3),
                 Skill("萬劍歸宗", 2.2, 4, 4), Skill("劍破虛空", 2.5, 5, 5)],
        "qiang": [Skill("槍芒刺", 1.4, 2, 1), Skill("龍槍突刺", 1.7, 3, 2, lambda p: setattr(p, 'combat_power', p.combat_power + 5)), 
                  Skill("破軍一擊", 2.0, 4, 3), Skill("天槍震地", 2.5, 5, 4)],
        "dan": [Skill("丹元護體", 0.5, 1, 1, lambda p: setattr(p, 'hp', min(p.hp + 20, 100))), 
                Skill("癒合丹術", 0, 5, 2, lambda p: setattr(p, 'hp', min(p.hp + 30, 100))),
                Skill("回春丹氣", 0.8, 3, 3, lambda p: setattr(p, 'hp', min(p.hp + 40, 100))), 
                Skill("丹道化生", 1.0, 4, 4, lambda p: setattr(p, 'hp', min(p.hp + 50, 100)))],
        "fa": [Skill("法符轟擊", 1.6, 2, 1), Skill("玄光波", 1.9, 3, 2), Skill("星辰隕落", 2.3, 4, 3), Skill("天法滅地", 2.7, 5, 4)]
    }
    
    skill_list_mo = {
        "xue": [Skill("血噬斬", 1.8, 2, 1, lambda p: setattr(p, 'hp', min(p.hp + 10, 100))), Skill("血氣爆", 2.0, 3, 2), 
                Skill("噬血狂擊", 2.4, 4, 3), Skill("血海吞天", 2.8, 5, 4)],
        "hun": [Skill("魂刺", 1.7, 2, 1), Skill("拘魂術", 1.9, 3, 2, lambda p: setattr(p, 'exp', p.exp + 5)), 
                Skill("魂爆", 2.3, 4, 3), Skill("魂鎖", 1.5, 4, 4, lambda p: setattr(p, 'enemy_damage_factor', 0.8)), 
                Skill("噬魂大法", 2.6, 5, 5)],
        "du": [Skill("毒霧", 1.5, 2, 1, lambda p: setattr(p, 'combat_power', max(p.combat_power - 5, 0))), Skill("腐毒擊", 1.8, 3, 2), 
               Skill("毒魂侵蝕", 2.3, 4, 3), Skill("萬毒噬心", 2.5, 5, 4)],
        "moyan": [Skill("焰噬", 1.9, 2, 1, lambda p: setattr(p, 'hp', max(p.hp - 5, 5) if p.hp > 5 else p.hp)), Skill("魔焰轟", 2.1, 3, 2), 
                  Skill("焚魂爆", 2.5, 4, 3), Skill("焰魔滅地", 2.9, 5, 4)]
    }
    
    sect_list = [
        Sect("天劍宗", lambda p: setattr(p, 'combat_power', p.combat_power + 20), "xian", "jian"),
        Sect("龍槍門", lambda p: (setattr(p, 'combat_power', p.combat_power + 15), setattr(p, 'hp', min(p.hp + 10, 100))), "xian", "qiang"),
        Sect("丹霞派", lambda p: setattr(p, 'elixirs', p.elixirs + 1) if p.sect_trigger_count % 3 == 0 else None, "xian", "dan"),
        Sect("玄法宗", lambda p: setattr(p, 'exp', p.exp + 10), "xian", "fa"),
        Sect("血魔宗", lambda p: setattr(p, 'combat_power', p.combat_power + 25), "mo", "xue"),
        Sect("幽魂教", lambda p: setattr(p, 'spirit_stones', p.spirit_stones + 20), "mo", "hun"),
        Sect("毒影門", lambda p: setattr(p, 'exp', p.exp + 15), "mo", "du"),
        Sect("魔焰殿", lambda p: (setattr(p, 'combat_power', p.combat_power + 20), setattr(p, 'hp', max(p.hp - 10, 1))), "mo", "moyan"),
        Sect("隱仙谷", lambda p: (setattr(p, 'combat_power', p.combat_power + 10), setattr(p, 'exp', p.exp + 5)), "both"),
        Sect("散修盟", lambda p: setattr(p, 'spirit_stones' if random.random() < 0.5 else 'elixirs', p.spirit_stones + 10 if random.random() < 0.5 else p.elixirs + 1), "both"),
    ]

    def __init__(self, name, path="xian", specialty="jian", realm_index=0, exp=0, next_breakthrough=100, spirit_stones=0, 
                 elixirs=0, techniques=None, treasure=None, faction=None, quests=None, 
                 combat_power=10, hp=100, weapon=None, armor=None, skills=None, sect_trigger_count=0, sect_quest=None):
        try:
            self.name = name
            self.path = path
            self.specialty = specialty
            self.realm_index = realm_index
            self.exp = exp
            self.next_breakthrough = next_breakthrough
            self.spirit_stones = spirit_stones
            self.elixirs = elixirs
            self.techniques = techniques if techniques is not None else []
            self.treasure = treasure if treasure is not None else []
            self.faction = faction
            self.quests = quests if quests is not None else []
            if sect_quest is None:
                task = random.choice(["擊敗敵人", "收集靈石", "修煉次數"])
                goal = 3 if task == "擊敗敵人" else 200 if task == "收集靈石" else 5
                self.sect_quest = {"task": task, "progress": 0, "goal": goal, "reward": "spirit_stones:50-100"}
            else:
                self.sect_quest = sect_quest
            self.combat_power = combat_power
            self.hp = hp
            self.sect_trigger_count = sect_trigger_count
            self.enemy_damage_factor = 1.0
            self.spirit_activate_count = 0
            self.injured = False
            self.action_log = []
            self.game_over = False  # 新增遊戲結束標記
            self.realms = self.realms_xian if path == "xian" else self.realms_mo
            # 使用 get() 確保武器與防具列表初始化正確
            self.weapon_list = self.weapon_list_xian.get(specialty, []) if path == "xian" else self.weapon_list_mo.get(specialty, [])
            self.armor_list = self.armor_list_xian.get(specialty, []) if path == "xian" else self.armor_list_mo.get(specialty, [])
            self.skill_list = self.skill_list_xian if path == "xian" else self.skill_list_mo
            # 初始化武器時檢查列表是否為空
            self.weapon = self.weapon_list[0] if weapon is None and self.weapon_list else weapon
            self.armor = armor
            self.skills = skills if skills is not None else []
            logging.info(f"玩家 {self.name} 初始化完成，路徑: {self.path}, 分支: {self.specialty}")
            if not self.weapon_list:
                logging.warning(f"警告: {self.path}-{self.specialty} 的武器列表為空")
            if not self.armor_list:
                logging.warning(f"警告: {self.path}-{self.specialty} 的防具列表為空")
        except Exception as e:
            logging.error(f"玩家初始化失敗: {str(e)}")
            raise

    def log_action(self, action):
        self.action_log.append(f"{time.ctime()}: {action}")
        logging.info(action)

    def apply_sect_effect(self):
        if self.faction:
            sect = next((s for s in self.sect_list if s.name == self.faction), None)
            if sect:
                self.sect_trigger_count += 1
                sect.effect(self)
                self.log_action(f"應用宗門 {self.faction} 效果")

    def get_total_attack(self):
        attack = self.combat_power + (self.weapon.get_attack() if self.weapon else 0)
        if self.path == "mo":
            heal = min(int(attack * 0.05), 100 - self.hp)
            if heal > 0:
                self.hp += heal
                print(f"魔修吸血 +{heal}")
        return attack

    def get_total_defense(self):
        return self.combat_power // 2 + (self.armor.defense if self.armor else 0)

    def cultivate(self):
        self.log_action("修煉")
        if self.injured:
            print("你身受重傷，無法修煉！")
            return
        gained_exp = random.randint(5, 15)
        self.exp += gained_exp
        print(f"修煉中… 獲得 {gained_exp} 修為")
        if self.faction and self.sect_quest["task"] == "修煉次數":
            self.sect_quest["progress"] += 1
            self.complete_quest()
        self.check_breakthrough()
        self.apply_sect_effect()

    def check_breakthrough(self):
        while self.exp >= self.next_breakthrough and self.realm_index < len(self.realms) - 1:
            self.exp -= self.next_breakthrough
            self.realm_index += 1
            self.next_breakthrough *= 2
            self.combat_power += random.randint(5, 10)
            print(f"\n✨ {self.name} 突破至 {self.realms[self.realm_index]}！戰力提升至 {self.combat_power}")
            self.log_action(f"突破至 {self.realms[self.realm_index]}")
            self.check_equipment_upgrade()
            self.check_skill_unlock()
        # 強制同步狀態
        self.hp = min(self.hp, 100)
        if self.faction:
            self.apply_sect_effect()

    def check_equipment_upgrade(self):
        self.log_action("檢查裝備升級")
        if self.weapon_list:
            max_weapon_index = len(self.weapon_list) - 1
            current_realm = min(self.realm_index, max_weapon_index)
            if self.realm_index >= 1 and self.weapon:
                required_stones = 50 * (self.weapon.required_realm + 1)
                if self.spirit_stones >= required_stones:
                    new_weapon = self.weapon_list[current_realm]
                    if new_weapon != self.weapon:
                        if self.weapon.spirit:
                            new_weapon.spirit = self.weapon.spirit
                            new_weapon.upgraded = self.weapon.upgraded
                            new_weapon.enhancements = self.weapon.enhancements
                            new_weapon.update_stats()
                        self.spirit_stones -= required_stones
                        print(f"↳ 武器升級：{new_weapon.name}，消耗 {required_stones} 靈石")
                        self.log_action(f"武器升級至 {new_weapon.name}，消耗 {required_stones} 靈石")
                        self.weapon = new_weapon
                else:
                    print(f"靈石不足 {required_stones}，無法升級武器！")
        
        if self.armor_list:
            max_armor_index = len(self.armor_list) - 1
            current_realm = min(self.realm_index, max_armor_index)
            if self.realm_index >= 1 and self.armor:
                required_stones = 50 * (self.armor.required_realm + 1)
                if self.spirit_stones >= required_stones:
                    new_armor = self.armor_list[current_realm]
                    if new_armor != self.armor:
                        self.spirit_stones -= required_stones
                        print(f"↳ 防具升級：{new_armor.name}，消耗 {required_stones} 靈石")
                        self.log_action(f"防具升級至 {new_armor.name}，消耗 {required_stones} 靈石")
                        self.armor = new_armor
                else:
                    print(f"靈石不足 {required_stones}，無法升級防具！")

    def check_skill_unlock(self):
        for skill in self.skill_list[self.specialty]:
            if skill.required_realm <= self.realm_index and skill not in self.skills:
                self.skills.append(skill)
                print(f"↳ 領悟技能：{skill.name}")
                self.log_action(f"領悟技能 {skill.name}")

    def encounter_event(self):
        self.log_action("探索")
        events = ["靈石", "丹藥", "門派", "敵人", "無事", "裝備", "技能", "奇遇", "器靈"]
        weights_xian = [15, 20, 20, 5, 15, 15, 5, 5, 1]
        weights_mo = [15, 10, 5, 10, 15, 15, 5, 5, 1]
        event = random.choices(events, weights=weights_xian if self.path == "xian" else weights_mo, k=1)[0]
        
        if event == "靈石":
            stones = random.randint(10, 50)
            self.spirit_stones += stones
            print(f"發現靈石 × {stones}")
            self.log_action(f"獲得 {stones} 靈石")
            if self.faction and self.sect_quest["task"] == "收集靈石":
                self.sect_quest["progress"] += stones
                self.complete_quest()
            self.apply_sect_effect()
        elif event == "丹藥":
            self.elixirs += 1
            print("獲得丹藥 × 1")
            self.log_action("獲得 1 丹藥")
            self.apply_sect_effect()
        elif event == "門派":
            if not self.faction:
                available_sects = [s for s in self.sect_list if s.allowed_path in [self.path, "both"] and (s.allowed_specialty is None or s.allowed_specialty == self.specialty)]
                if available_sects:
                    sect = random.choice(available_sects)
                    self.faction = sect.name
                    self.sect_trigger_count = 0
                    self.sect_quest["task"] = random.choice(["擊敗敵人", "收集靈石", "修煉次數"])
                    self.sect_quest["progress"] = 0
                    self.sect_quest["goal"] = 3 if self.sect_quest["task"] == "擊敗敵人" else 200 if self.sect_quest["task"] == "收集靈石" else 5
                    self.sect_quest["reward"] = random.choice(["spirit_stones:50-100", "exp:100-200", "elixirs:1-2"])
                    self.apply_sect_effect()
                    print(f"加入 {sect.name}，獲得宗門加成與任務：{self.sect_quest['task']} ({self.sect_quest['goal']})")
                    self.log_action(f"加入宗門 {sect.name}")
                else:
                    print("無適合你的宗門招募")
            else:
                print(f"已是 {self.faction} 成員")
        elif event == "敵人":
            if not self.weapon:
                print("你沒有武器，無法戰鬥，返回主選單")
                self.log_action("無武器，跳過戰鬥")
            else:
                self.battle()
        elif event == "裝備":
            self.find_equipment()
        elif event == "技能":
            self.find_skill()
        elif event == "奇遇":
            if random.random() < 0.5:
                stones = random.randint(20, 100)
                self.spirit_stones += stones
                print(f"奇遇：發現秘藏，獲得靈石 × {stones}")
                self.log_action(f"奇遇獲得 {stones} 靈石")
                if self.faction and self.sect_quest["task"] == "收集靈石":
                    self.sect_quest["progress"] += stones
                    self.complete_quest()
            else:
                exp = random.randint(10, 50)
                self.exp += exp
                print(f"奇遇：參悟天機，獲得修為 × {exp}")
                self.log_action(f"奇遇獲得 {exp} 修為")
        elif event == "器靈":
            if not self.weapon:
                print("你尚未擁有武器，無法附著器靈！")
            elif not self.weapon.spirit:
                spirit = Spirit(random.choice(["青龍", "朱雀", "白虎", "玄武"]))
                self.weapon.spirit = spirit
                self.weapon.update_stats()
                print(f"奇遇：{spirit.name}器靈附著，你的武器 {self.weapon.name} 得到增強！")
                self.log_action(f"獲得器靈 {spirit.name}")
            else:
                print("你的武器已有器靈，無事發生")
        else:
            print("探索無收穫…")
            self.log_action("探索無收穫")

    def find_equipment(self):
        self.log_action("尋找裝備")
        if random.random() < 0.5 and self.weapon_list:
            weapon = random.choice(self.weapon_list[min(self.realm_index + 1, len(self.weapon_list) - 1)])
            print(f"發現 {weapon.name}")
            if not self.weapon or weapon.required_realm > (self.weapon.required_realm if self.weapon else -1):
                self.weapon = weapon
                print(f"已裝備 {weapon.name}")
                self.log_action(f"裝備 {weapon.name}")
            else:
                stones = weapon.min_attack * 2
                self.spirit_stones += stones
                print(f"出售獲 {stones} 靈石")
                self.log_action(f"出售裝備獲 {stones} 靈石")
                if self.faction and self.sect_quest["task"] == "收集靈石":
                    self.sect_quest["progress"] += stones
                    self.complete_quest()
        elif self.armor_list:
            armor = random.choice(self.armor_list[min(self.realm_index + 1, len(self.armor_list) - 1)])
            print(f"發現 {armor.name}")
            if not self.armor or armor.required_realm > (self.armor.required_realm if self.armor else -1):
                self.armor = armor
                print(f"已裝備 {armor.name}")
                self.log_action(f"裝備 {armor.name}")
            else:
                stones = armor.defense * 2
                self.spirit_stones += stones
                print(f"出售獲 {stones} 靈石")
                self.log_action(f"出售防具獲 {stones} 靈石")
                if self.faction and self.sect_quest["task"] == "收集靈石":
                    self.sect_quest["progress"] += stones
                    self.complete_quest()

    def find_skill(self):
        self.log_action("尋找技能")
        available_skills = [s for s in self.skill_list[self.specialty] if s not in self.skills and s.required_realm <= self.realm_index]
        if available_skills:
            skill = random.choice(available_skills)
            self.skills.append(skill)
            print(f"領悟 {skill.name}")
            self.log_action(f"領悟技能 {skill.name}")
        else:
            print("無新技能可學")

    def battle(self):
        if not self.weapon:
            print("你沒有武器，無法戰鬥！")
            self.log_action("無武器，無法戰鬥")
            return
        
        enemy_path = random.choice(["xian", "mo"])
        enemy_specialty = random.choice(["jian", "qiang", "dan", "fa"] if enemy_path == "xian" else ["xue", "hun", "du", "moyan"])
        enemy_type = random.choice(["普通", "高防", "低攻"])
        base_power = max(self.combat_power, random.randint(self.combat_power, self.combat_power + 20))
        if self.realm_index >= 5:
            base_power = int(base_power * 1.2)

        if enemy_type == "普通":
            enemy_power = base_power
            enemy_defense = int(enemy_power * 0.6)
            enemy_skill = "增益"
        elif enemy_type == "高防":
            enemy_power = int(base_power * 0.8)
            enemy_defense = int(enemy_power * 0.65)
            enemy_skill = "防禦"
        else:
            enemy_power = int(base_power * 1.2)
            enemy_defense = enemy_power // 3
            enemy_skill = "治療"
        
        if self.realm_index >= 5:
            enemy_hp = random.randint(int(enemy_power * 1.5), enemy_power * 3)
        else:
            enemy_hp = int(enemy_power * 1.5) if enemy_type == "普通" else int(enemy_power * 1.8) if enemy_type == "高防" else enemy_power
        enemy_max_hp = enemy_hp
        
        skill_list = self.skill_list_xian[enemy_specialty] if enemy_path == "xian" else self.skill_list_mo[enemy_specialty]
        enemy_skills = [s for s in skill_list if s.required_realm <= self.realm_index]
        if not enemy_skills:
            enemy_skills = [Skill("普通攻擊", 1.0, 0, 0)]
        enemy_skills = random.sample(enemy_skills, min(2, len(enemy_skills)))
        
        print(f"\n⚔ 遭遇{enemy_path.capitalize()}-{enemy_specialty.capitalize()} {enemy_type}敵人 戰力: {enemy_power} 血量: {enemy_hp}")
        self.log_action(f"遭遇{enemy_path}-{enemy_specialty} {enemy_type}敵人 (戰力: {enemy_power}, 血量: {enemy_hp})")

        self.spirit_activate_count = 0
        while enemy_hp > 0 and self.hp > 0:
            print(f"\n你 [{self.hp}/100] | 敵 [{enemy_hp}/{enemy_max_hp}]")
            print("1. 攻擊  2. 技能  3. 丹藥  4. 靈石激發  5. 跑路")
            choice = input("> ").strip()
            
            if choice == "1":
                damage = max(1, self.get_total_attack() - enemy_defense)
                enemy_hp -= damage
                print(f"攻擊造成 {damage} 傷害")
                self.log_action(f"攻擊敵人，造成 {damage} 傷害")
            elif choice == "2":
                if not self.skills:
                    print("無技能可用")
                    self.log_action("嘗試使用技能，但無技能可用")
                    continue
                print("技能：")
                for i, s in enumerate(self.skills[:4]):
                    cd = f"({s.current_cooldown})" if s.current_cooldown > 0 else ""
                    print(f"{i+1}. {s.name} {cd}")
                if len(self.skills) > 4:
                    print("...更多技能")
                try:
                    skill_choice = int(input("> ").strip()) - 1
                    if 0 <= skill_choice < len(self.skills):
                        enemy_hp, success = self.skills[skill_choice].apply(self, enemy_hp)
                        self.log_action(f"使用技能 {self.skills[skill_choice].name}" + ("成功" if success else "失敗"))
                        if not success:
                            continue
                    else:
                        print("選擇無效")
                        self.log_action("技能選擇無效")
                        continue
                except ValueError:
                    print("輸入錯誤")
                    self.log_action("技能輸入錯誤")
                    continue
            elif choice == "3":
                self.use_elixir()
            elif choice == "4":
                self.spirit_activate()
            elif choice == "5":
                if self.spirit_stones >= 50:
                    self.spirit_stones -= 50
                    if random.random() < 0.8:
                        print("跑路成功！你脫離了戰鬥！消耗 50 靈石")
                        self.log_action("跑路成功，消耗 50 靈石")
                        return
                    else:
                        print("跑路失敗！敵人攔住了你！消耗 50 靈石")
                        self.log_action("跑路失敗，消耗 50 靈石")
                        enemy_damage = max(1, int(random.randint(enemy_power // 2, enemy_power) * self.enemy_damage_factor) - self.get_total_defense())
                        self.hp -= enemy_damage
                        print(f"敵人反擊，損失 {enemy_damage} 血量（僅普通攻擊）")
                        self.log_action(f"跑路失敗，敵人普通攻擊，損失 {enemy_damage} 血量")
                elif self.elixirs >= 5:
                    self.elixirs -= 5
                    if random.random() < 0.8:
                        print("跑路成功！你脫離了戰鬥！消耗 5 顆丹藥")
                        self.log_action("跑路成功，消耗 5 顆丹藥")
                        return
                    else:
                        print("跑路失敗！敵人攔住了你！消耗 5 顆丹藥")
                        self.log_action("跑路失敗，消耗 5 顆丹藥")
                        enemy_damage = max(1, int(random.randint(enemy_power // 2, enemy_power) * self.enemy_damage_factor) - self.get_total_defense())
                        self.hp -= enemy_damage
                        print(f"敵人反擊，損失 {enemy_damage} 血量（僅普通攻擊）")
                        self.log_action(f"跑路失敗，敵人普通攻擊，損失 {enemy_damage} 血量")
                elif self.hp > 50:
                    self.hp -= 50
                    if random.random() < 0.8:
                        print("跑路成功！你脫離了戰鬥！損失 50 血量")
                        self.log_action("跑路成功，損失 50 血量")
                        return
                    else:
                        print("跑路失敗！敵人攔住了你！損失 50 血量")
                        self.log_action("跑路失敗，損失 50 血量")
                        enemy_damage = max(1, int(random.randint(enemy_power // 2, enemy_power) * self.enemy_damage_factor) - self.get_total_defense())
                        self.hp -= enemy_damage
                        print(f"敵人反擊，損失 {enemy_damage} 血量（僅普通攻擊）")
                        self.log_action(f"跑路失敗，敵人普通攻擊，損失 {enemy_damage} 血量")
                else:
                    print("靈石、丹藥不足，且血量低於 50，無法跑路！")
                    self.log_action("跑路失敗，資源不足")
                    continue
            else:
                print("無效選擇")
                self.log_action("戰鬥選擇無效")
                continue

            if enemy_hp <= 0:
                stones = random.randint(10, 50)
                self.spirit_stones += stones
                print(f"\n勝利！獲得 30 修為與 {stones} 靈石")
                self.log_action(f"戰鬥勝利，獲得 30 修為與 {stones} 靈石")
                self.exp += 30
                if random.random() < 0.001:
                    if random.random() < 0.5 and self.weapon_list:
                        drop = random.choice(self.weapon_list[:self.realm_index + 1])
                        print(f"敵人掉落武器：{drop.name}")
                        self.log_action(f"敵人掉落武器 {drop.name}")
                        if not self.weapon or drop.required_realm > self.weapon.required_realm:
                            self.weapon = drop
                            print(f"已裝備 {drop.name}")
                    elif self.armor_list:
                        drop = random.choice(self.armor_list[:self.realm_index + 1])
                        print(f"敵人掉落防具：{drop.name}")
                        self.log_action(f"敵人掉落防具 {drop.name}")
                        if not self.armor or drop.required_realm > self.armor.required_realm:
                            self.armor = drop
                            print(f"已裝備 {drop.name}")
                self.check_breakthrough()
                if self.faction and self.sect_quest["task"] == "擊敗敵人":
                    self.sect_quest["progress"] += 1
                    self.complete_quest()
                return

            if random.random() < 0.5:
                if enemy_skill == "增益" and enemy_power < base_power * 1.5:
                    enemy_power = int(enemy_power * 1.2)
                    print("敵人使用增益，戰力提升！")
                    self.log_action("敵人使用增益")
                elif enemy_skill == "防禦":
                    enemy_defense = int(enemy_defense * 1.5)
                    print("敵人使用防禦，防禦力提升！")
                    self.log_action("敵人使用防禦")
                elif enemy_skill == "治療" and enemy_hp < enemy_max_hp:
                    heal = int(enemy_max_hp * 0.2)
                    enemy_hp = min(enemy_hp + heal, enemy_max_hp)
                    print(f"敵人使用治療，恢復 {heal} 血量！")
                    self.log_action(f"敵人治療，恢復 {heal} 血量")
            if random.random() < 0.5 and enemy_skills:
                skill = random.choice(enemy_skills)
                damage = int(enemy_power * skill.damage_factor)
                self.hp -= max(1, damage - self.get_total_defense())
                print(f"敵人使用 {skill.name}，你損失 {damage} 血量！")
                self.log_action(f"敵人使用 {skill.name}，損失 {damage} 血量")
            
            enemy_damage = max(1, int(random.randint(enemy_power // 2, enemy_power) * self.enemy_damage_factor) - self.get_total_defense())
            self.hp -= enemy_damage
            print(f"敵人反擊，損失 {enemy_damage} 血量")
            self.log_action(f"敵人反擊，損失 {enemy_damage} 血量")
            
            if random.random() < 0.000001 and not self.injured:
                self.injured = True
                print("⚠ 你受到嚴重傷害，無法修煉！")
                self.log_action("受到嚴重傷害")

            if self.hp <= 0:
                print("\n戰敗！你已殞地")
                self.save_game_log("戰敗殞地")
                self.game_over = True
                return

            for skill in self.skills:
                skill.update_cooldown()
            self.apply_sect_effect()
            self.enemy_damage_factor = 1.0
            time.sleep(0.5)

    def find_fight(self):
        self.log_action("找人打架")
        if random.random() < 0.99999999:
            if not self.weapon:
                print("你沒有武器，無法戰鬥！")
                self.log_action("無武器，跳過戰鬥")
            else:
                self.battle()
        else:
            print("沒人理你...")
            self.log_action("找人打架但沒人理")

    def show_probabilities(self):
        self.log_action("查看概率")
        events = ["靈石", "丹藥", "門派", "敵人", "無事", "裝備", "技能", "奇遇", "器靈"]
        weights_xian = [15, 20, 20, 5, 15, 15, 5, 5, 1]
        weights_mo = [15, 10, 5, 10, 15, 15, 5, 5, 1]
        total_xian = sum(weights_xian)
        total_mo = sum(weights_mo)
        
        print("\n=== 事件概率 ===")
        print("探索事件 (仙修):")
        for event, weight in zip(events, weights_xian):
            prob = (weight / total_xian) * 100
            print(f"{event}: {prob:.2f}%")
        print("\n探索事件 (魔修):")
        for event, weight in zip(events, weights_mo):
            prob = (weight / total_mo) * 100
            print(f"{event}: {prob:.2f}%")
        print("\n找人打架:")
        print(f"遭遇敵人: 99.999999%")
        print(f"沒人理你: 0.000001%")

    def complete_quest(self):
        if self.sect_quest["progress"] >= self.sect_quest["goal"]:
            reward = self.sect_quest["reward"].split(":")
            if reward[0] == "spirit_stones":
                amount = random.randint(int(reward[1].split("-")[0]), int(reward[1].split("-")[1]))
                self.spirit_stones += amount
                print(f"宗門任務完成！獎勵靈石 × {amount}")
                self.log_action(f"完成宗門任務，獲得 {amount} 靈石")
            elif reward[0] == "exp":
                amount = random.randint(int(reward[1].split("-")[0]), int(reward[1].split("-")[1]))
                self.exp += amount
                print(f"宗門任務完成！獎勵修為 × {amount}")
                self.log_action(f"完成宗門任務，獲得 {amount} 修為")
            elif reward[0] == "elixirs":
                amount = random.randint(int(reward[1].split("-")[0]), int(reward[1].split("-")[1]))
                self.elixirs += amount
                print(f"宗門任務完成！獎勵丹藥 × {amount}")
                self.log_action(f"完成宗門任務，獲得 {amount} 丹藥")
            self.sect_quest = {
                "task": random.choice(["擊敗敵人", "收集靈石", "修煉次數"]),
                "progress": 0,
                "goal": 3 if self.sect_quest["task"] == "擊敗敵人" else 200 if self.sect_quest["task"] == "收集靈石" else 5,
                "reward": random.choice(["spirit_stones:50-100", "exp:100-200", "elixirs:1-2"])
            }
            print(f"獲得新任務：{self.sect_quest['task']} ({self.sect_quest['goal']})")
            self.log_action(f"獲得新任務：{self.sect_quest['task']} ({self.sect_quest['goal']})")

    def use_elixir(self):
        self.log_action("使用丹藥")
        if self.hp >= 100:
            print("血量已滿，無需使用丹藥！")
            return
        if self.elixirs > 0:
            self.elixirs -= 1
            heal = random.randint(20, 50)
            self.hp = min(self.hp + heal, 100)
            print(f"使用丹藥，恢復 {heal} 血量")
            self.log_action(f"使用丹藥，恢復 {heal} 血量")
            self.apply_sect_effect()
        else:
            print("無丹藥可用")

    def spirit_activate(self):
        self.log_action("嘗試靈石激發")
        if not self.skills or not any(skill.current_cooldown > 0 for skill in self.skills):
            print("無技能冷卻中，無法使用靈石激發！")
            return
        if self.spirit_stones >= 50 and self.spirit_activate_count < 3:
            self.spirit_stones -= 50
            self.spirit_activate_count += 1
            for skill in self.skills:
                if skill.current_cooldown > 0:
                    skill.current_cooldown -= 1
            print("靈石激發成功，技能冷卻減少 1 回合，靈石 -50")
            self.log_action("靈石激發成功，消耗 50 靈石")
        elif self.spirit_activate_count >= 3:
            print("此戰鬥已達靈石激發上限")
        else:
            print("靈石不足，無法激發！")

    def upgrade_spirit(self):
        self.log_action("嘗試器靈進階")
        if not self.weapon:
            print("你尚未擁有武器，無法進階器靈！")
            return
        if not self.weapon.spirit:
            print("你的武器無器靈，無法進階！")
            return
        if self.weapon.upgraded:
            print("器靈已進階")
            return
        if self.spirit_stones >= 500:
            self.spirit_stones -= 500
            self.weapon.upgraded = True
            self.weapon.update_stats()
            print(f"器靈 {self.weapon.spirit.name} 進階成功，武器加成提升至 30%，靈石 -500")
            self.log_action(f"器靈 {self.weapon.spirit.name} 進階，消耗 500 靈石")
        else:
            print("靈石不足，無法進階器靈")

    def heal_injury(self):
        self.log_action("嘗試修復重傷")
        if not self.injured:
            print("你未受重傷，無需修復！")
            return False
        if self.spirit_stones < 1000:
            print("靈石不足 1000，去賺吧！")
            return False
        
        if self.realm_index >= 3:
            self.realm_index -= 3
            self.spirit_stones -= 1000
            self.injured = False
            self.combat_power = max(10, self.combat_power - 15)
            print(f"修復重傷成功，跌落 3 個境界，損失 1000 靈石！當前境界：{self.realms[self.realm_index]}")
            self.log_action(f"修復重傷成功，跌落 3 個境界，消耗 1000 靈石")
            return True
        else:
            print(f"境界不足 3 個（當前：{self.realms[self.realm_index]}），是否強行修復？成功率 10%，仍需 1000 靈石 (y/n)")
            choice = input("> ").strip()
            if choice == "y":
                self.spirit_stones -= 1000
                if random.random() < 0.1:
                    self.injured = False
                    print("強行修復成功，損失 1000 靈石！")
                    self.log_action("強行修復重傷成功，消耗 1000 靈石")
                    return True
                else:
                    print("強行修復失敗，你因重傷不治而亡！")
                    self.log_action("強行修復重傷失敗")
                    self.save_game_log("重傷修復失敗")
                    self.game_over = True
                    return False
            else:
                print("取消修復重傷")
                return False

    def leave_sect(self):
        self.log_action("離開宗門")
        if self.faction:
            print(f"你離開了 {self.faction}")
            self.faction = None
            self.sect_trigger_count = 0
            self.sect_quest["progress"] = 0
            self.sect_quest["reward"] = None
        else:
            print("你未加入任何宗門")

    def buy_item(self, choice):
        self.log_action(f"嘗試購買商店物品: {choice}")
        prices = {
            '1': 50,  # 丹藥
            '2': 100,  # 武器碎片
            '3': 300,  # 技能書
            '4': 1000  # 進階石
        }
        if choice not in prices:
            print("無效選擇")
            self.log_action("購買失敗，選擇無效")
            return
        
        cost = prices[choice]
        if self.spirit_stones < cost:
            print(f"靈石不足，需要 {cost} 靈石")
            self.log_action(f"購買失敗，靈石不足 {cost}")
            return
        
        if choice == "1":
            self.spirit_stones -= cost
            self.elixirs += 1
            print("購買丹藥成功！")
            self.log_action("購買丹藥成功，消耗 50 靈石")
        elif choice == "2":
            if not self.weapon:
                print("你沒有武器，無法使用武器碎片！")
                self.log_action("購買失敗，無武器")
                return
            self.spirit_stones -= cost
            self.weapon.base_min_attack += 5
            self.weapon.base_max_attack += 5
            self.weapon.update_stats()
            print(f"購買武器碎片成功！武器 {self.weapon.name} 攻擊力提升至 {self.weapon.min_attack}-{self.weapon.max_attack}")
            self.log_action(f"購買武器碎片成功，消耗 100 靈石")
        elif choice == "3":
            available_skills = [s for s in self.skill_list[self.specialty] if s not in self.skills and s.required_realm <= self.realm_index + 1]
            if not available_skills:
                print("無可學習的新技能，購買取消")
                self.log_action("無新技能可學，購買取消")
                return
            self.spirit_stones -= cost
            skill = random.choice(available_skills)
            self.skills.append(skill)
            print(f"購買技能書成功！領悟 {skill.name}")
            self.log_action(f"購買技能書成功，領悟 {skill.name}，消耗 300 靈石")
        elif choice == "4":
            if not self.weapon:
                print("你沒有武器，無法使用進階石！")
                self.log_action("購買失敗，無武器")
                return
            self.spirit_stones -= cost
            self.weapon.base_min_attack += 20
            self.weapon.base_max_attack += 20
            self.weapon.update_stats()
            print(f"購買進階石成功！武器 {self.weapon.name} 攻擊力提升至 {self.weapon.min_attack}-{self.weapon.max_attack}")
            self.log_action(f"購買進階石成功，消耗 1000 靈石")

    def save_game_log(self, cause_of_death):
        log_file = os.path.join(os.path.dirname(__file__), "遊戲日誌.txt")
        score = (self.realm_index * 10) + (self.spirit_stones * 0.01) + (50 if self.weapon and self.weapon.spirit else 0)
        with open(log_file, "w", encoding="utf-8") as f:
            f.write("=== 遊戲日誌 ===\n")
            f.write(f"玩家名稱: {self.name}\n")
            f.write("行動記錄:\n")
            for action in self.action_log:
                f.write(f"{action}\n")
            f.write(f"\n死因: {cause_of_death}\n")
            f.write(f"最終評分: {score:.2f}\n")
            f.write(f"最終境界: {self.realms[self.realm_index]}\n")
            f.write(f"最終靈石: {self.spirit_stones}\n")
            f.write(f"器靈: {'有' if self.weapon and self.weapon.spirit else '無'}\n")
        print(f"遊戲日誌已生成於 {log_file}")

    def save(self):
        self.log_action("存檔")
        try:
            save_dir = r"D:\自製遊戲"
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
                print(f"資料夾 {save_dir} 不存在，已自動創建")
            temp_filename = os.path.join(save_dir, "修仙模擬器.json.tmp")
            save_filename = os.path.join(save_dir, "修仙模擬器.json")
            with open(temp_filename, "w", encoding="utf-8") as f:
                data = self.__dict__.copy()
                weapon_data = None
                if self.weapon:
                    weapon_data = {k: v for k, v in self.weapon.__dict__.items() if k != 'spirit'}
                    if self.weapon.spirit:
                        weapon_data['spirit'] = self.weapon.spirit.__dict__
                data['weapon'] = weapon_data
                data['armor'] = self.armor.__dict__ if self.armor else None
                data['skills'] = [s.__dict__.copy() for s in self.skills]
                del data['realms']
                del data['weapon_list']
                del data['armor_list']
                del data['skill_list']
                del data['sect_list']
                json.dump(data, f, indent=4, ensure_ascii=False)
            os.replace(temp_filename, save_filename)
            print("存檔完成")
        except Exception as e:
            print(f"保存過程中發生錯誤：{str(e)}")
            self.log_action(f"存檔失敗：{str(e)}")

    @classmethod
    def load(cls):
        try:
            save_dir = r"D:\自製遊戲"
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
                print(f"資料夾 {save_dir} 不存在，已自動創建，返回新遊戲")
                return None
            save_filename = os.path.join(save_dir, "修仙模擬器.json")
            with open(save_filename, "r", encoding="utf-8") as f:
                data = json.load(f)
            valid_keys = inspect.getfullargspec(cls.__init__).args[1:]
            filtered_data = {k: v for k, v in data.items() if k in valid_keys}
            data.setdefault('sect_quest', {"task": "擊敗敵人", "progress": 0, "goal": 3, "reward": "spirit_stones:50-100"})
            data.setdefault('action_log', [])
            data.setdefault('game_over', False)  # 確保載入時有 game_over 字段
            path = data.get('path', 'xian')
            specialty = data.get('specialty', 'jian' if path == 'xian' else 'xue')
            weapon_list = cls.weapon_list_xian if path == "xian" else cls.weapon_list_mo
            armor_list = cls.armor_list_xian if path == "xian" else cls.armor_list_mo
            skill_list = cls.skill_list_xian if path == "xian" else cls.skill_list_mo
            weapon_data = data.get('weapon')
            if weapon_data:
                if 'spirit' in weapon_data:
                    spirit = Spirit(weapon_data['spirit']['name'])
                    weapon = Weapon(**{k: v for k, v in weapon_data.items() if k != 'spirit'}, spirit=spirit)
                else:
                    weapon = Weapon(**weapon_data)
            else:
                weapon = None
            armor_data = data.get('armor')
            armor = Armor(**armor_data) if armor_data else None
            skills = []
            for s_data in data.get('skills', []):
                skill = Skill(**{k: v for k, v in s_data.items() if k != 'effect'})
                skill.effect = next((s.effect for s in skill_list[specialty] if s.name == skill.name), None)
                skills.append(skill)
            instance = cls(**filtered_data, weapon=weapon, armor=armor, skills=skills)
            instance.apply_sect_effect()
            logging.info(f"成功加載存檔，玩家: {instance.name}")
            return instance
        except Exception as e:
            print(f"加載失敗：{str(e)}，返回新遊戲")
            logging.error(f"加載存檔失敗：{str(e)}")
            return None

def main():
    player = Player.load()
    if not player:
        name = input("取個名字吧: ")
        print("\n選擇修煉路徑：")
        print("1. 仙修 - 正道飛升")
        print("2. 魔修 - 霸道魔帝")
        while True:
            path_choice = input("> ").strip()
            if path_choice in ["1", "2"]:
                path = "xian" if path_choice == "1" else "mo"
                break
            print("請輸入 1 或 2")
        
        if path == "xian":
            print("\n選擇分支：")
            print("1. 劍修 - 高攻單體")
            print("2. 槍修 - 範圍防禦")
            print("3. 丹修 - 治療恢復")
            print("4. 法修 - 遠程爆發")
            while True:
                specialty_choice = input("> ").strip()
                specialty = {"1": "jian", "2": "qiang", "3": "dan", "4": "fa"}.get(specialty_choice)
                if specialty:
                    break
                print("請輸入 1-4")
        else:
            print("\n選擇分支：")
            print("1. 血修 - 吸血生存")
            print("2. 魂修 - 靈魂控制")
            print("3. 毒修 - 減益敵人")
            print("4. 魔焰修 - 高攻代價")
            while True:
                specialty_choice = input("> ").strip()
                specialty = {"1": "xue", "2": "hun", "3": "du", "4": "moyan"}.get(specialty_choice)
                if specialty:
                    break
                print("請輸入 1-4")
        
        player = Player(name, path, specialty)
    
    while not player.game_over:
        print("\n=== 修仙之路 ===")
        print("1. 修煉  2. 探索  3. 狀態  4. 丹藥  5. 存檔  6. 退出  7. 離開宗門  8. 商店  9. 器靈進階  10. 修復重傷  11. 找人打架  12. 查看概率")
        choice = input("> ").strip()
        
        if choice == "1":
            player.cultivate()
        elif choice == "2":
            player.encounter_event()
        elif choice == "3":
            print("\n狀態查看：1. 基礎  2. 裝備  3. 技能與任務")
            page = input("> ").strip()
            if page == "1":
                print(f"\n=== {player.name} ===")
                print(f"路徑: {'仙修' if player.path == 'xian' else '魔修'}")
                specialty_display = {"jian": "劍修", "qiang": "槍修", "dan": "丹修", "fa": "法修",
                                     "xue": "血修", "hun": "魂修", "du": "毒修", "moyan": "魔焰修"}
                print(f"分支: {specialty_display[player.specialty]}")
                print(f"境界: {player.realms[player.realm_index]}")
                print(f"修為: {player.exp}/{player.next_breakthrough}")
                print(f"戰力: {player.combat_power} | 血量: {player.hp}/100")
                print(f"靈石: {player.spirit_stones} | 丹藥: {player.elixirs}")
                print(f"重傷狀態: {'是' if player.injured else '否'}")
            elif page == "2":
                print(f"\n=== 裝備 ===")
                weapon_str = f"武器: {player.weapon.name} ({player.weapon.min_attack}-{player.weapon.max_attack})" if player.weapon else "武器: 無"
                if player.weapon and player.weapon.spirit:
                    weapon_str += f" (器靈: {player.weapon.spirit.name}{' 已進階' if player.weapon.upgraded else ''})"
                print(weapon_str)
                armor_str = f"防具: {player.armor.name} ({player.armor.defense})" if player.armor else "防具: 無"
                print(armor_str)
            elif page == "3":
                print(f"\n=== 技能與任務 ===")
                skill_str = ", ".join([f"{s.name}({s.current_cooldown})" if s.current_cooldown > 0 else s.name for s in player.skills[:4]]) + ("..." if len(player.skills) > 4 else "") if player.skills else "無"
                print(f"技能: {skill_str}")
                quest_str = f"{player.sect_quest['task']} ({player.sect_quest['progress']}/{player.sect_quest['goal']}) 獎勵: {player.sect_quest['reward']}" if player.faction else "無"
                print(f"門派: {player.faction or '無'} | 任務: {quest_str}")
            else:
                print("無效選擇")
        elif choice == "4":
            player.use_elixir()
        elif choice == "5":
            player.save()
        elif choice == "6":
            player.save()
            print("已退出")
            break
        elif choice == "7":
            player.leave_sect()
        elif choice == "8":
            print("\n商店：")
            print("1. 丹藥 (50 靈石)")
            print("2. 武器碎片 (100 靈石，+5 基礎攻擊)")
            print("3. 技能書 (300 靈石，隨機技能)")
            print("4. 進階石 (1000 靈石，+20 基礎攻擊)")
            shop_choice = input("> ").strip()
            player.buy_item(shop_choice)
        elif choice == "9":
            player.upgrade_spirit()
        elif choice == "10":
            player.heal_injury()
        elif choice == "11":
            player.find_fight()
        elif choice == "12":
            player.show_probabilities()
        else:
            print("請選有效選項")
        
        if player.game_over:
            print("遊戲結束，請重新開始或退出")
            break
        
        time.sleep(0.5)

if __name__ == "__main__":
    main()