#!/usr/bin/env python3
"""
冷凍空調工程技師 歷屆試題下載器

用法:
  python download-exams.py          # 下載所有未完成年份 (100-114)
  python download-exams.py 113      # 只下載 113 年
  python download-exams.py 110 114  # 下載 110~114 年
"""
import os, re, sys, urllib.parse, subprocess

# ── 已知考試代碼（無需重新查詢）────────────────────────
YEAR_CODES = {
    100: "100230", 101: "101180", 102: "102180",
    103: "103170", 104: "104170", 105: "105170",
    106: "106180", 107: "107180", 108: "108180",
    109: "109180", 110: "110180", 111: "111180",
    112: "112190", 113: "113190", 114: "114180",
}

# 科目名稱關鍵字 → 檔名（優先匹配：長字串先）
SUBJECT_MAP = [
    ("冷凍空調自動控制", "automatic-control"),
    ("電工學",          "electrical-engineering"),
    ("熱力學",          "thermodynamics"),
    ("流體力學",        "fluid-mechanics"),
    ("冷凍工程",        "refrigeration-engineering"),
    ("空調工程",        "air-conditioning-engineering"),
]

BASE_SEARCH = "https://wwwq.moex.gov.tw/exam/wFrmExamQandASearch.aspx"
BASE_FILE   = "https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx"


def curl_get(url):
    r = subprocess.run(["curl", "-sk", url],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.stdout


def curl_post(url, data):
    r = subprocess.run(["curl", "-sk", url,
                        "-H", "Content-Type: application/x-www-form-urlencoded",
                        "--data", urllib.parse.urlencode(data)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.stdout


def extract_viewstate(html):
    def g(pat):
        m = re.search(pat, html)
        return m.group(1) if m else ""
    return {
        "__VIEWSTATE":          g(r'id="__VIEWSTATE"\s+value="([^"]+)"'),
        "__VIEWSTATEGENERATOR": g(r'id="__VIEWSTATEGENERATOR"\s+value="([^"]+)"'),
        "__VIEWSTATEENCRYPTED": "",
        "__EVENTVALIDATION":    g(r'id="__EVENTVALIDATION"\s+value="([^"]+)"'),
    }


def get_subject_codes(roc_year, exam_code):
    """
    3-step ASP.NET 表單 POST，回傳 {filename: s值}
    解析方式：checkbox ID = chk_{code}_009_{s}，比 href regex 更可靠
    """
    gregorian = roc_year + 1911

    html1 = curl_get(BASE_SEARCH)

    html2 = curl_post(BASE_SEARCH, {
        **extract_viewstate(html1),
        "ctl00$holderContent$wUctlExamYearStart$ddlExamYear": str(gregorian),
        "ctl00$holderContent$wUctlExamYearEnd$ddlExamYear":   str(gregorian),
        "ctl00$holderContent$ddlExamCode": "",
        "ctl00$holderContent$btnYear": "依考試年度設定考試簡稱",
    })

    html3 = curl_post(BASE_SEARCH, {
        **extract_viewstate(html2),
        "ctl00$holderContent$wUctlExamYearStart$ddlExamYear": str(gregorian),
        "ctl00$holderContent$wUctlExamYearEnd$ddlExamYear":   str(gregorian),
        "ctl00$holderContent$ddlExamCode": exam_code,
        "ctl00$holderContent$btnSearch": "查詢",
    })

    idx = html3.find("冷凍空調工程技師")
    if idx == -1:
        return {}
    section = html3[idx:idx + 8000]

    result = {}
    pairs = re.findall(
        r'chk_\d+_009_(\d+)"[^/]*/><.*?class="exam-title">(.*?)</label>',
        section, re.DOTALL)
    for s_val, name in pairs:
        for keyword, filename in SUBJECT_MAP:
            if keyword in name and filename not in result:
                result[filename] = s_val
                break
    return result


def download_year(roc_year, out_dir):
    exam_code = YEAR_CODES[roc_year]
    print(f"\n[{roc_year}年] code={exam_code}")

    print("  查詢科目代碼...", end=" ", flush=True)
    subjects = get_subject_codes(roc_year, exam_code)
    if not subjects:
        print("✗ 找不到冷凍空調工程技師，跳過")
        return False
    print(f"找到 {len(subjects)} 科")

    year_dir = os.path.join(out_dir, str(roc_year))
    os.makedirs(year_dir, exist_ok=True)

    success = 0
    for filename, s_val in subjects.items():
        out_path = os.path.join(year_dir, f"{filename}.pdf")
        if os.path.exists(out_path) and os.path.getsize(out_path) > 10000:
            print(f"  ✓ {filename}.pdf (已存在)")
            success += 1
            continue
        url = f"{BASE_FILE}?t=Q&code={exam_code}&c=009&s={s_val}&q=1"
        subprocess.run(["curl", "-sk", "-L", url, "-o", out_path], capture_output=True)
        size = os.path.getsize(out_path) if os.path.exists(out_path) else 0
        if size > 10000:
            print(f"  ✓ {filename}.pdf ({size // 1024} KB)")
            success += 1
        else:
            print(f"  ✗ {filename}.pdf 下載失敗 (size={size})")

    return success == len(subjects)


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(script_dir, "exam-papers")

    if len(sys.argv) == 3:
        years = list(range(int(sys.argv[1]), int(sys.argv[2]) + 1))
    elif len(sys.argv) == 2:
        years = [int(sys.argv[1])]
    else:
        years = sorted(YEAR_CODES.keys())

    # 跳過已完成年份
    pending = []
    for y in years:
        if y not in YEAR_CODES:
            print(f"{y}年：無對應考試代碼（115年尚未開放）")
            continue
        year_dir = os.path.join(out_dir, str(y))
        existing = len([f for f in os.listdir(year_dir) if f.endswith(".pdf")]) \
                   if os.path.exists(year_dir) else 0
        if existing >= 6:
            print(f"{y}年：已完成，跳過")
        else:
            pending.append(y)

    if not pending:
        print("\n所有年份已下載完畢！")
        return

    results = {}
    for year in pending:
        results[year] = download_year(year, out_dir)

    print(f"\n{'='*40}")
    print("本次下載結果：")
    for year, ok in results.items():
        print(f"  {year}年: {'✓ 完成' if ok else '✗ 失敗'}")


if __name__ == "__main__":
    main()
