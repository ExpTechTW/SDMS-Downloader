import requests
import os
import zipfile
import shutil
from tqdm import tqdm
import time

num = input("輸入檢知編號: ")

if os.path.exists("./output"):
    shutil.rmtree("./output")

folder_path_list = ["./output", "./output/x-sac", "./output/y-sac", "./output/z-sac",
                    "./output/waveform", "./output/composite", "./output/dayplot", "./output/cache"]
for folder_path in folder_path_list:
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

if num.isdigit():
    url = 'https://exptech.com.tw/api/v1/earthquake/trem-info/{}'.format(
        num)
    response = requests.get(url)
    if (response.status_code == 200):
        response = response.json()

        with tqdm(total=len(response["station"]), desc="進度") as pbar:
            start = response["alert"]-10000
            end = response["alert"]+240000

            for i in response["station"]:
                station = i["uuid"]
                url = 'https://exptech.com.tw/api/v1/trem/waveform?station={}&start={}&end={}'.format(
                    station, start, end)
                tqdm.write("開始 [打包] 測站 {} 資料...".format(station))
                response = requests.get(url)

                if (response.status_code == 200):
                    tqdm.write("測站 {} 資料 [打包] 完成".format(station))
                    url = 'https://exptech.com.tw/api/v1/file/Download/{}.zip'.format(
                        response.text)
                    tqdm.write("開始 [下載] 測站 {} 資料...".format(station))
                    response = requests.get(url)
                    if (response.status_code == 200):
                        tqdm.write("測站 {} 資料 [下載] 完成".format(station))
                        tqdm.write("開始 [儲存] 測站 {} 資料...".format(station))
                        with open('./output/cache/{}.zip'.format(station), 'wb') as file:
                            file.write(response.content)
                        tqdm.write("測站 {} 資料 [儲存] 完成".format(station))
                        tqdm.write("開始 [解壓縮] 測站 {} 資料...".format(station))
                        with zipfile.ZipFile('./output/cache/{}.zip'.format(station), 'r') as zip_ref:
                            zip_ref.extractall(
                                "./output/cache/{}".format(station))
                        tqdm.write("測站 {} 資料 [解壓縮] 完成".format(station))
                        tqdm.write("開始 [整理] 測站 {} 資料...".format(station))
                        shutil.move("./output/cache/{}/X.sac".format(station),
                                    "./output/x-sac/{}.sac".format(station))
                        shutil.move("./output/cache/{}/Y.sac".format(station),
                                    "./output/y-sac/{}.sac".format(station))
                        shutil.move("./output/cache/{}/Z.sac".format(station),
                                    "./output/z-sac/{}.sac".format(station))
                        shutil.move("./output/cache/{}/waveform.png".format(station),
                                    "./output/waveform/{}.png".format(station))
                        shutil.move("./output/cache/{}/dayplot.png".format(station),
                                    "./output/dayplot/{}.png".format(station))
                        shutil.move("./output/cache/{}/composite.png".format(station),
                                    "./output/composite/{}.png".format(station))
                        tqdm.write("測站 {} 資料 [整理] 完成".format(station))
                        pbar.update(1)
                    else:
                        tqdm.write(
                            "Error => 測站 {} 資料 [下載] 失敗!".format(station))
                        pbar.update(1)
                else:
                    tqdm.write("Error => 測站 {} 資料 [打包] 失敗!".format(station))
                    pbar.update(1)
        if os.path.exists("./output/cache"):
            shutil.rmtree("./output/cache")
    else:
        print("查無此編號的地震")
else:
    print("您輸入的不是一個數字")
