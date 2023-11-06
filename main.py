import requests
from bs4 import BeautifulSoup
from collections import defaultdict
import re

# ウェブページのURL
url = "https://densuke.biz/list?cd=eUVfLVfQAX3a4ZyN"

# ウェブページからHTMLを取得
response = requests.get(url)
html = response.content

# BeautifulSoupでHTMLを解析
soup = BeautifulSoup(html, "html.parser")

# 出席者情報が含まれる表を見つける
table = soup.find("table", {"class": "listtbl"})

# 出席状況をカウントするための辞書
attendance_count = defaultdict(lambda: defaultdict(int))

# 出席者情報を抽出
rows = table.find_all("tr")  # 全ての行を取得
place = rows[1].find_all("td")[0].get_text(strip=True)  # 1行目の1列目に場所が書いてある
sum_attendance = rows[1].find_all("td")[1].get_text(strip=True)  # 1行目の2列目に出席者数が書いてある
sun_tbd = (
    rows[1].find_all("td")[2].get_text(strip=True)
)  # 特にビジネスシーンで「TBD、TBA、TBC」という略語表現が使われます。 これらは「To be decided」

# 各楽器ごとの出席者数をカウント
for i in range(0, len(rows), 2):  # 2行ずつ処理（楽器名行と出席状況行）
    instruments_row = rows[i]
    status_row = rows[i + 1] if (i + 1) < len(rows) else None

    # 楽器名行から楽器名を取得
    instrument_cells = instruments_row.find_all("td")[4:]  # 楽器名は5番目のセル以降にある
    instrument_names = [cell.get_text(strip=True) for cell in instrument_cells]

    # 出席状況行から出席状況を取得
    if status_row:
        status_cells = status_row.find_all("td")[4:]  # 出席状況は5番目のセル以降にある
        statuses = [cell.get_text(strip=True) for cell in status_cells]

        # 楽器名と出席状況を関連付けてカウント
        for instrument_name, status in zip(instrument_names, statuses):
            # ピリオドを無視し、T.saxとTsaxを同一視する
            instrument_name = instrument_name.replace(".", "").replace("Tsax", "T.sax")
            # 楽器名を抽出（アルファベットの後に日本語が続くパターン）
            instrument_match = re.match(r"([A-Za-z\s]+).*", instrument_name)
            if instrument_match:
                instrument = instrument_match.group(1).strip()
                attendance_count[instrument][status] += 1

print(place, "の出席者は")
# 各楽器ごとの出席者数を出力
for instrument, counts in attendance_count.items():
    print(
        # f"{instrument}: ○ 出席: {counts.get('○', 0)}人, △ 未定: {counts.get('△', 0)}人, × 不参加: {counts.get('×', 0)}人"
        f"{instrument}: ○ 出席: {counts.get('○', 0)}人, △ 未定: {counts.get('△', 0)}人"
    )
print(f"出席: {sum_attendance}人", f"未定: {sun_tbd}人", sep=", ")
