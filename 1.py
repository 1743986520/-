import random
import webbrowser
import time

def greet():
    print("電腦部署本地 AI 要嗎？")
    m = input("")
    if m == "要":
        print("電腦瀏覽器輸入 https://ollama.com，等他安裝完，打開 cmd 輸入 `ollama`，輸入你要的模型代號ollama run deepseek-r1:7b")
        G = input("需不需要幫助，回答要或不要:")
        if G == "要":
            webbrowser.open_new("https://ollama.com/download/OllamaSetup.exe")
        else:
            print("OK")
    else:
        print("那算了")
        print("愛要不要")


題庫 = ["鮑恩慶要不要打", "鮑恩慶要不要罰", "鮑恩慶要不要凌遲"]

print("鮑恩慶是不是豬？")  
a = input("最好回答是：") 

while a != "是":
    print("Are you ok?")
    a = input("最好回答是：")

print("真棒")
print("恭喜您通過驗證，接下來請設定暱稱\n")
name = input("")
print(f"歡迎你，{name}")

random_item = random.choice(題庫)
print("\n請回答下列問題：")
print(random_item)
a = input("回答 '要' 或 '不要'：")

if a == "要":
    print("不是臥底")
    print("最近臥底很多")
    print("地址是：https://sites.google.com/view/yellow-game/%E9%A6%96%E9%A0%81")
    print("別的窩點：https://www.iwara.tv/video/iDKSHB4D8nvjTn")
    
    a = input("要更刺激的嗎？回答 '要' 或 '不要'：")

    if a == "要":
        print("想的美")
        print("好吧，給你\n")
        greet()
    else:
        print("那就好")
        greet()
else:
    print("你個臥底直接槍斃")
    print("碰(槍聲)")
    print("你已死亡")
    time.sleep(10)
    webbrowser.open_new("https://encrypted-tbn1.gstatic.com/images?q=tbn:ANd9GcT5egd2Qe5sUlmb78bRV7alyJ1VfnKz2D46G6WIwd2ES4vtFRAZdEMZhQ2EvV1MpfhtK37YcyXiL8uGoRFdGcqbf4MTliWGg-DMZLE7zA")#補上朝唪
    time.sleep(99999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999)