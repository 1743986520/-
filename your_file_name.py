# -*- coding: utf-8 -*-
import os
import re
import json
import difflib
from datetime import datetime
import pytesseract
from PIL import ImageGrab
import pyautogui
import psutil
from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer

# 🧠 指定 Tesseract 的執行檔路徑（請確認你的實際安裝路徑）
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

class SmartAssistant:
    def __init__(self):
        self.memory_path = os.path.expanduser("~/SmartAssistant")
        os.makedirs(self.memory_path, exist_ok=True)

        self._load_models()
        self.long_memory = self._load_json("memory.json", default={"conversations":[]})
        self.skill_lib = self._load_json("skills.json", default={
            "time": {
                "patterns": ["现在几点", "当前时间", "几点钟了"],
                "action": lambda: f"🕒 现在是 {datetime.now().strftime('%H:%M')}"
            },
            "date": {
                "patterns": ["今天几号", "现在日期", "今天是"],
                "action": lambda: f"📅 今天是 {datetime.now().strftime('%Y年%m月%d日')}"
            }
        })

        print("💡 智能助理已就绪！尝试说：'写个倒计时程序' 或 '截图保存到桌面'")

    def _load_models(self):
        self.nlp_tokenizer = AutoTokenizer.from_pretrained("uer/t5-small-chinese-cluecorpussmall")
        self.nlp_model = AutoModelForSeq2SeqLM.from_pretrained("uer/t5-small-chinese-cluecorpussmall")
        self.pattern_engine = {
            'code': ["写代码", "编程", "写个程序"],
            'file': ["打开文件", "查看文档", "找一下"],
            'media': ["播放", "暂停", "音量"]
        }

    def _load_json(self, filename, default=None):
        path = os.path.join(self.memory_path, filename)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return default if default else {}

    def _save_json(self, filename, data):
        with open(os.path.join(self.memory_path, filename), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _understand(self, text):
        for skill, data in self.skill_lib.items():
            if any(patt in text for patt in data["patterns"]):
                return skill

        for category, patterns in self.pattern_engine.items():
            if any(patt in text for patt in patterns):
                return category

        closest = difflib.get_close_matches(text, [p for skill in self.skill_lib.values() for p in skill["patterns"]], n=1)
        if closest:
            return next((k for k,v in self.skill_lib.items() if closest[0] in v["patterns"]), None)

        inputs = self.nlp_tokenizer(f"理解意图: {text}", return_tensors="pt")
        outputs = self.nlp_model.generate(inputs.input_ids)
        return self.nlp_tokenizer.decode(outputs[0], skip_special_tokens=True)

    def _execute(self, intent, text):
        builtin = {
            'code': lambda: self._generate_code(text),
            'screenshot': lambda: self._take_screenshot(text),
            'search': lambda: self._search_memory(text)
        }

        if intent in self.skill_lib:
            return self.skill_lib[intent]["action"]()

        if intent in builtin:
            return builtin[intent]()

        return "🤔 我不太确定您的意思，请换种说法试试？"

    def _generate_code(self, request):
        lang = "Python" if "python" in request.lower() else ""
        prompt = f"用{lang}写一个{request.replace('写', '').replace('代码', '')}"

        samples = {
            "倒计时": "import time\nfor i in range(5,0,-1):\n    print(i); time.sleep(1)",
            "计算器": "result = eval(input('输入算式: '))\nprint(f'结果是: {result}')"
        }

        closest = difflib.get_close_matches(request, samples.keys(), n=1)
        return f"```{lang}\n{samples[closest[0]] if closest else '# 代码生成功能待扩展'}\n```"

    def _take_screenshot(self, text):
        path = os.path.join(os.path.expanduser("~"), "Desktop/screenshot.png")
        ImageGrab.grab().save(path)
        return f"📸 截图已保存到桌面 (路径: {path})"

    def process(self, text):
        if text.startswith("学习"):
            try:
                _, pattern, action = text.split("|")
                new_skill = {
                    "patterns": [pattern.strip()],
                    "action": eval(f"lambda: {action.strip()}")
                }
                self.skill_lib[f"custom_{len(self.skill_lib)}"] = new_skill
                self._save_json("skills.json", self.skill_lib)
                return f"🎯 已学会: 当你说'{pattern}'时，我会执行: {action}"
            except:
                return "学习格式: 学习|触发词|执行动作"

        intent = self._understand(text)
        response = self._execute(intent, text)

        self.long_memory["conversations"].append({
            "time": datetime.now().isoformat(),
            "input": text,
            "intent": intent,
            "response": response
        })

        return response

if __name__ == "__main__":
    ai = SmartAssistant()
    print("""\n💬 交互指南:
1. 直接说需求 (例: "设置5点提醒")
2. 教新技能 (例: "学习|打开音乐|os.system('start spotify')")
3. 输入 exit 退出""")
    
    while True:
        try:
            user_input = input("\n您: ").strip()
            if user_input.lower() in ["exit", "退出"]:
                ai._save_json("memory.json", ai.long_memory)
                print("🛑 助理已退出")
                break
                
            if user_input:
                response = ai.process(user_input)
                print(f"助理: {response}")
                
        except KeyboardInterrupt:
            ai._save_json("memory.json", ai.long_memory)
            print("\n⚠️ 对话已保存")
            break
