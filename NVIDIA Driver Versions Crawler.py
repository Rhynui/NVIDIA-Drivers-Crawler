from email.headerregistry import ContentTypeHeader
from time import sleep
import random
from requests import get
from bs4 import BeautifulSoup as bs

URL_START = "https://www.nvidia.com/download/driverResults.aspx/"
DOWNLOAD_URL_DOMAIN = "https://www.nvidia.com"

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36"

HEADERS = {"User-Agent" : USER_AGENT}

LANGUAGE_CODE = {
    "English (US)": "en-us",
    "English (UK)": "en-uk",
    "English (India)": "en-in",
    "Chinese (Simplified)": "cn",
    "Chinese (Traditional)": "tw",
    "Japanese": "jp",
    "Korean": "kr",
    "Deutsch": "de",
    "Español (España)": "es",
    "Español (América Latina)": "la",
    "Français": "fr",
    "Italiano": "it",
    "Polski": "pl",
    "Português (Brazil)": "br",
    "Русский": "ru",
    "Turkish": "tr",
    "Other": "en-uk",
}

MAX_ERROR_COUNT = 400  # the maximum count of consecutive error pages untill the program exit
SAVE_AFTER_COUNT = 1000  # the number of entries wrote into the file before saving

TITLE_SELECTER = "table .pageTitle"
VERSION_SELECTER = "#tdVersion"
DATE_SELECTER = "#tdReleaseDate"
OS_SELECTER = "table table:first-of-type tr:nth-child(3) .contentsummaryright"
LANGUAGE_SELECTER = "table table:first-of-type tr:nth-child(5) .contentsummaryright"
SIZE_SELECTER = "table table:first-of-type tr:nth-child(6) .contentsummaryright"
SUPPORTED_GPU_SELECTER = "#half-spaced"
LINK_SELECTER = "#lnkDwnldBtn"


file = open("E:/NVIDIA Drivers.csv", "r", encoding="UTF-8")
try:
    line = file.readlines()[-1]
    id = int(line[:line.find(',')]) + 1
except:
    id = 0
file.close()

file = open("E:/NVIDIA Drivers.csv", "a", encoding="UTF-8")
write_count = 0
# id = 0
error_count = 0
while error_count < MAX_ERROR_COUNT:
    print()
    # print("Sleeping...")
    # sleep(random.uniform(0, 0.5))
    print("Requesting {}...".format(id))
    timeout_count = 1
    page_link = URL_START+str(id)
    while True:
        try:
            page_html = get(page_link, headers=HEADERS, timeout=5)
            break
        except:
            print("Request timed out x{}.".format(timeout_count))
            sleep(timeout_count)
            timeout_count += 1

    print("Parsing {} for language...".format(id))
    page = bs(page_html.content, "lxml")
    try:
        language = page.select_one(LANGUAGE_SELECTER).get_text(strip=True)
    except:
        print("{} page error.".format(id))
        error_count += 1
        id += 1
        continue

    print("Parsing {} for size...".format(id))
    page = bs(page_html.content, "lxml")
    try:
        size = page.select_one(SIZE_SELECTER).get_text(strip=True)
        if not size.endswith("KB") and not size.endswith("MB") and size != "Temporarily unavailable" and size != "null":
            raise Exception("\"{}\" unknown size".format(size))
    except:
        print("{} page error.".format(id))
        error_count += 1
        id += 1
        continue

    print("Requesting {} again...".format(id))
    timeout_count = 1
    code = ""
    for lang in LANGUAGE_CODE:
        if language.startswith(lang):
            code = LANGUAGE_CODE[lang]
            break
    page_link += "/" + code
    while True:
        try:
            page_html = get(page_link, headers=HEADERS, timeout=5)
            break
        except:
            print("Request timed out x{}.".format(timeout_count))
            sleep(timeout_count)
            timeout_count += 1

    print("Parsing {}...".format(id))
    page = bs(page_html.content, "lxml")
    version_text = page.select_one(VERSION_SELECTER).get_text('|', True)
    index = version_text.find('|')
    if index != -1:
        version = version_text[:index]
        version_type = version_text[index+1:]
    else:
        version = version_text
        version_type = ""
    
    title = page.select_one(TITLE_SELECTER).get_text(strip=True)
    
    date = page.select_one(DATE_SELECTER).get_text(strip=True).replace('.', '-')

    os = page.select_one(OS_SELECTER).get_text(strip=True)

    size = page.select_one(SIZE_SELECTER).get_text(strip=True)
    if not size.endswith("KB") and not size.endswith("MB"):
        size = "N/A"

    supported_gpu = ", ".join(map(lambda x: x.get_text(), page.select(SUPPORTED_GPU_SELECTER)))

    download_link = DOWNLOAD_URL_DOMAIN + page.select_one(LINK_SELECTER).get("href")

    dch = "No" if download_link.find("dch") == -1 else "Yes" 

    file.write("{},\"{}\",\"{}\",\"{}\",\"{}\",{},\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\"\n".format(id, title, version, version_type, dch, date, os, language, size, supported_gpu, page_link, download_link))
    write_count += 1
    if write_count > SAVE_AFTER_COUNT:
        write_count = 0
        file.close()
        sleep(1)
        file = open("E:/NVIDIA Drivers.csv", "a", encoding="UTF-8")

    error_count = 0
    id += 1

print("Too many consecutive errors, exiting...")
file.close()
