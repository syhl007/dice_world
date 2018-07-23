import random
import re


class WordFilter:

    @staticmethod
    def handle(text):
        return text


class DiceFilter:

    @staticmethod
    def handle(text):
        dice = re.compile(r'^\.([1-9][0-9]*)?[dD]([1-9][0-9]*)(\s)*(.+)?$')
        coc_create = re.compile(r'^\.new(\s)coc$')
        dnd_create = re.compile(r'^\.[new|NEW](\s)[dnd|DND]$')
        text_group = dice.match(text)
        if text_group:
            if text_group.group(1):
                dice_num = int(text_group.group(1))
            else:
                dice_num = 1
            dice_face = 1 if int(text_group.group(2)) == 0 else int(text_group.group(2))
            if text_group.group(4):
                reason = text_group.group(4)
            else:
                reason = '测手气'
            dice_list = [random.randint(1, dice_face) for i in range(dice_num)]
            total = sum(dice_list)
            text = '因为【' + reason + '】骰出：' + str(dice_list) + '=' + str(total)
            return text
        text_group = coc_create.match(text)
        if text_group:
            STR = sum([random.randint(1, 6) for i in range(3)])
            CON = sum([random.randint(1, 6) for i in range(3)])
            POW = sum([random.randint(1, 6) for i in range(3)])
            DEX = sum([random.randint(1, 6) for i in range(3)])
            APP = sum([random.randint(1, 6) for i in range(3)])
            SIZ = sum([random.randint(1, 6) for i in range(2)]) + 6
            INT = sum([random.randint(1, 6) for i in range(2)]) + 6
            EDU = sum([random.randint(1, 6) for i in range(3)]) + 3
            SAN = POW * 5
            IDEA = INT * 5
            LUCK = POW * 5
            KNOW = EDU * 5
            HP = int((CON + SIZ) / 2)
            MP = POW
            DB_data = SIZ + STR
            if 2 <= DB_data <= 12:
                DB = '-1d6'
            elif 13 <= DB_data <= 16:
                DB = '-1d4'
            elif 17 <= DB_data <= 24:
                DB = '+0'
            elif 25 <= DB_data <= 32:
                DB = '+1d4'
            elif 33 <= DB_data <= 40:
                DB = '+1d6'
            elif 41 <= DB_data <= 56:
                DB = '+2d6'
            elif 57 <= DB_data <= 72:
                DB = '+3d6'
            elif 73 <= DB_data <= 88:
                DB = '+4d6'
            else:
                DB = '0'
            MONEY = random.randint(1, 10)
            text = []
            text.append("<br> 创建了一个COC人物：")
            text.append("<br>———————基础属性———————")
            text.append("<br>力量：" + str(STR))
            text.append("<br>体质：" + str(CON))
            text.append("<br>意志：" + str(POW))
            text.append("<br>敏捷：" + str(DEX))
            text.append("<br>外表：" + str(APP))
            text.append("<br>体型：" + str(SIZ))
            text.append("<br>智力：" + str(INT))
            text.append("<br>教育：" + str(EDU))
            text.append("<br>———————派生属性———————")
            text.append("<br>灵感：" + str(IDEA))
            text.append("<br>幸运：" + str(LUCK))
            text.append("<br>知识：" + str(KNOW))
            text.append("<br>伤害加深：" + str(DB))
            text.append("<br>HP：" + str(HP))
            text.append("<br>MP：" + str(MP))
            text.append("<br>SAN：" + str(SAN))
            text.append("<br>资产：" + str(MONEY))
            return ''.join(text)
