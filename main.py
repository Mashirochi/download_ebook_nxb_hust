import os
import requests
from PIL import Image
from bs4 import BeautifulSoup
import re
import unicodedata
import sys
import time
from variable import book_url, GA, VISITOR, ANTIFORGERY, AUTH, GA_TRACK
import random

### CẤU HÌNH CHƯƠNG TRÌNH ###
# Cấu hình chuẩn của tớ nếu mọi người thích thay đổi gì tự đổi True/False nhé
DOWNLOAD_IMAGE = True  # 🔥 đổi thành False nếu bạn đã có ảnh và chỉ muốn tạo PDF
SHOULD_MERGE_TO_PDF = True  # 🔥 bật/tắt gộp PDF (merge image to pdf)
DELETE_FOLDER_AFTER_MERGE = True  # 🔥 bật/tắt xóa folder sau khi merge PDF xong
ENABLE_FAILED_IMAGE = False  # 🔥 True/False/None: False = skip merge nếu có 5 ảnh lỗi liên tiếp, True/None = chạy hết rồi merge
DEBUG_PROGRAM = False  # 🔥 True để giữ lại các file tạm, False để xóa
MAKE_COLOR = True  # 🔥 Làm màu
CONVERT_FILE_NAMES_TO_SLUG = True  # 🔥 True để chuyển tên file PDF thành dạng slug
X_NO_RETRY = 2  # 🔥 Số lần retry khi lấy tham số từ ebook link (thử /0/1 trước, nếu lỗi thì thử link gốc)
#
###

### THAM SỐ NẾU LỖI KHI CHẠY CHƯƠNG TRÌNH ###
# Tên pdf sau khi merge thành công (để trống hoặc "result.pdf" để tự động lấy từ title)
output_pdf = "result.pdf"
manual_ebook_link = ""
total_pages = 0
# Cách lấy base_url
# Làm bước 0 như ảnh buoc_0.png rồi xem video
base_url = ""
id_sach = ""
# Thư mục lưu tạm các image bạn tải
save_dir = "img"
###

### Từ đoạn dưới trở đi nếu không rành code thì đừng sửa gì nhé ###
# ===== ANSI COLORS =====
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
CYAN = "\033[36m"
MAGENTA = "\033[35m"
RESET = "\033[0m"


def animated_print(text, color="", duration=5):
    """Print text with a crypto-style animation, showing characters one by one"""
    if not MAKE_COLOR:
        print(f"{color}{text}{RESET}")
        return

    chars = list(text)
    if len(chars) > 0:
        delay = duration / len(chars)

        for char in chars:
            sys.stdout.write(f"{color}{char}{RESET}")
            sys.stdout.flush()
            time.sleep(delay)

        print()


def cleanup_temp_files():
    if not DEBUG_PROGRAM:
        temp_files = ["raw.html", "temp.js"]
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
                if DEBUG_PROGRAM:
                    print(f"{MAGENTA}🗑 Đã xóa file tạm: {temp_file}{RESET}")


def build_cookies():
    cookies = {}
    if GA:
        cookies["_ga"] = GA
    if VISITOR:
        cookies["visitorId"] = VISITOR
    if ANTIFORGERY:
        cookies[".AspNetCore.Antiforgery.PAnxZgrQbk8"] = ANTIFORGERY
    if AUTH:
        cookies["auth"] = AUTH
    if GA_TRACK:
        cookies["_ga_HFDYKEJJ3N"] = GA_TRACK
    return cookies


def validate_cookies():
    if not GA and not VISITOR and not ANTIFORGERY and not AUTH and not GA_TRACK:
        print(f"{RED}❌ Lỗi: Vui lòng điền cookie{RESET}")
        print(f"{YELLOW}💡 Hướng dẫn: Control shift I => Application => Cookies => https://nxbbachkhoa.vn/{RESET}")
        exit(1)


def get_ebook_info_from_book_url(book_url):
    if DEBUG_PROGRAM:
        print(f"{YELLOW}📖 Đang lấy thông tin từ URL sách...{RESET}")

    response = requests.get(book_url)
    response.encoding = response.apparent_encoding
    soup = BeautifulSoup(response.text, "html.parser")
    with open("raw.html", "w", encoding=response.encoding) as f:
        f.write(soup.prettify())

    if not DEBUG_PROGRAM and os.path.exists("raw.html"):
        os.remove("raw.html")

    ebook_info = {}

    ebook_section = soup.find("div", class_="BookDetailSection-actions")
    if ebook_section:
        ebook_links = ebook_section.find_all("a", href=re.compile(r"/ebook/\d+"))

        short_link = None
        long_link = None

        for link in ebook_links:
            href = link["href"]
            if re.match(r"/ebook/\d+/.+", href):
                long_link = href
            else:
                short_link = href

        selected_ebook_link = long_link if long_link else short_link

        if selected_ebook_link:
            if selected_ebook_link.startswith("/"):
                selected_ebook_link = "https://nxbbachkhoa.vn" + selected_ebook_link

            ebook_info["link_ebook"] = selected_ebook_link

    page_count = None

    details_section = soup.find("div", class_="details-table-list")
    if details_section:
        page_elements = details_section.find_all(string=re.compile(r"Số trang"))
        for element in page_elements:
            parent = element.parent
            if parent:
                next_elements = parent.find_next_siblings()
                for next_el in next_elements:
                    text = next_el.get_text(strip=True)
                    if text.isdigit():
                        page_count = text
                        break
            if page_count:
                break

    if not page_count:
        html_text = str(soup)
        page_match = re.search(r"Số trang[^>]*>[\s]*<td[^>]*>[\s]*(\d+)", html_text)
        if page_match:
            page_count = page_match.group(1)

    if not page_count:
        all_text = soup.get_text()
        page_match = re.search(r"Số trang[^\d]*(\d+)", all_text)
        if page_match:
            page_count = page_match.group(1)

    ebook_info["page_count"] = page_count

    title_tag = soup.find("title")
    if title_tag:
        title = title_tag.get_text(strip=True)
        ebook_info["title"] = title

    return ebook_info


def get_id_sach_from_ebook_link(ebook_link, cookies):
    if DEBUG_PROGRAM:
        print(f"{YELLOW}🔍 Đang lấy id_sach từ link ebook...{RESET}")

    base_ebook_link = re.sub(r"(/ebook/\d+)(/.*)?$", r"\1", ebook_link)
    link_with_suffix = base_ebook_link + "/0/1"
    link_without_suffix = base_ebook_link
    last_error = None

    for attempt in range(X_NO_RETRY):
        for link in [link_with_suffix, link_without_suffix]:
            try:
                response = requests.get(link, cookies=cookies, timeout=10)

                if response.status_code != 200:
                    if link == link_with_suffix:
                        if DEBUG_PROGRAM:
                            print(f"{YELLOW}⚠️  Link với /0/1 lỗi (Status {response.status_code}), thử link gốc...{RESET}")
                        continue
                    else:
                        continue

                soup = BeautifulSoup(response.text, "html.parser")
                script_tag = soup.find("script", src=re.compile(r"mobile/javascript/config\.js"))

                if script_tag:
                    script_url = script_tag["src"]

                    if script_url.startswith("//"):
                        script_url = "https:" + script_url
                    elif script_url.startswith("/"):
                        script_url = "https://nxbbachkhoa.vn" + script_url

                    script_response = requests.get(script_url, cookies=cookies)
                    content = script_response.text

                    match = re.search(r'bookConfig\.CreatedTime\s*=\s*"?(\d+)"?', content)

                    if match:
                        if link == link_without_suffix:
                            print(f"{GREEN}✓ Tìm thấy id_sach từ link gốc (không có /0/1): {link}{RESET}")
                        return match.group(1)
                else:
                    if link == link_with_suffix:
                        if DEBUG_PROGRAM:
                            print(f"{YELLOW}⚠️  Link với /0/1 không có script config, thử link gốc...{RESET}")
                        continue
            except Exception as e:
                last_error = e
                if link == link_with_suffix:
                    if DEBUG_PROGRAM:
                        print(f"{YELLOW}⚠️  Link với /0/1 lỗi: {e}, thử link gốc...{RESET}")
                    continue
                else:
                    break

        if attempt < X_NO_RETRY - 1:
            if DEBUG_PROGRAM:
                print(f"{YELLOW}⚠️  Retry lần {attempt + 2}/{X_NO_RETRY}...{RESET}")
            time.sleep(1)

    if last_error:
        error_msg = f"Không thể lấy id_sach từ ebook link sau {X_NO_RETRY} lần thử. Lỗi cuối: {last_error}"
        print(f"{RED}❌ {error_msg}{RESET}")
        raise Exception(error_msg)

    return None


def get_base_url_from_ebook_link(ebook_link, cookies):
    """Lấy base_url từ link ebook, tự động thử /0/1 trước, nếu lỗi thì retry với link gốc"""
    if DEBUG_PROGRAM:
        print(f"{YELLOW}🔗 Đang lấy base_url từ link ebook...{RESET}")

    headers = {"User-Agent": "Mozilla/5.0"}

    base_ebook_link = re.sub(r"(/ebook/\d+)(/.*)?$", r"\1", ebook_link)
    link_with_suffix = base_ebook_link + "/0/1"
    link_without_suffix = base_ebook_link

    last_error = None

    for attempt in range(X_NO_RETRY):
        for link in [link_with_suffix, link_without_suffix]:
            try:
                response = requests.get(link, headers=headers, cookies=cookies, timeout=10)

                if response.status_code != 200:
                    if link == link_with_suffix:
                        if DEBUG_PROGRAM:
                            print(f"{YELLOW}⚠️  Link với /0/1 lỗi (Status {response.status_code}), thử link gốc...{RESET}")
                        continue
                    else:
                        continue

                html = response.text
                urls = re.findall(r'https?://[^\s"\'<>]+', html)

                mobile_urls = {u for u in urls if "/files/mobile" in u}

                if mobile_urls:
                    if link == link_without_suffix:
                        print(f"{GREEN}✓ Tìm thấy base_url từ link gốc (không có /0/1): {link}{RESET}")
                    return list(mobile_urls)[0]
                else:
                    if link == link_with_suffix:
                        if DEBUG_PROGRAM:
                            print(f"{YELLOW}⚠️  Link với /0/1 không có mobile URL, thử link gốc...{RESET}")
                        continue
            except Exception as e:
                last_error = e
                if link == link_with_suffix:
                    if DEBUG_PROGRAM:
                        print(f"{YELLOW}⚠️  Link với /0/1 lỗi: {e}, thử link gốc...{RESET}")
                    continue
                else:
                    break

        if attempt < X_NO_RETRY - 1:
            if DEBUG_PROGRAM:
                print(f"{YELLOW}⚠️  Retry lần {attempt + 2}/{X_NO_RETRY}...{RESET}")
            time.sleep(1)
    if last_error:
        error_msg = f"Không thể lấy base_url từ ebook link sau {X_NO_RETRY} lần thử. Lỗi cuối: {last_error}"
        print(f"{RED}❌ {error_msg}{RESET}")
        raise Exception(error_msg)

    return None


def crypto_print(text, color=CYAN, speed=0.02, noise_level=10):
    charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%&*?"

    for final_char in text:
        current_char = random.choice(charset)

        for _ in range(noise_level):
            sys.stdout.write(f"{color}{current_char}{RESET}")
            sys.stdout.flush()
            time.sleep(speed)
            sys.stdout.write("\b")
            current_char = random.choice(charset)

        sys.stdout.write(f"{color}{final_char}{RESET}")
        sys.stdout.flush()
        time.sleep(speed)

    print()


def auto_fill_parameters():
    """Tự động điền các tham số nếu chúng rỗng"""
    global total_pages, base_url, id_sach, book_url, output_pdf

    validate_cookies()
    cookies = build_cookies()

    need_info = not total_pages or total_pages == 0 or not base_url or not id_sach or not book_url

    if not need_info:
        if DEBUG_PROGRAM:
            print(f"{GREEN}✓ Tất cả tham số đã được điền, bỏ qua bước tự động lấy thông tin{RESET}")
        return

    if not book_url:
        print(f"{RED}❌ Vui lòng điền book_url để tự động lấy thông tin{RESET}")
        return

    if DEBUG_PROGRAM:
        print(f"{CYAN}🔄 Bắt đầu tự động lấy thông tin...{RESET}\n")

    ebook_info = get_ebook_info_from_book_url(book_url)
    ebook_link = ebook_info.get("link_ebook")

    if not total_pages and ebook_info.get("page_count"):
        total_pages = int(ebook_info["page_count"])
        if DEBUG_PROGRAM:
            print(f"{GREEN}✓ Số trang: {total_pages}{RESET}")

    if not ebook_link:
        if ebook_info.get("page_count"):
            if manual_ebook_link:
                ebook_link = manual_ebook_link
                if DEBUG_PROGRAM:
                    print(f"{YELLOW}⚠️  Không tìm thấy link ebook tự động, sử dụng link thủ công{RESET}")
                    print(f"{GREEN}✓ Link ebook (thủ công): {ebook_link}{RESET}")
            else:
                if DEBUG_PROGRAM:
                    print(f"{YELLOW}⚠️  Không tìm thấy link ebook tự động{RESET}")
                    print(f"{YELLOW}💡 Bạn có thể điền manual_ebook_link nếu có số trang{RESET}")
                if base_url and id_sach:
                    if DEBUG_PROGRAM:
                        print(f"{GREEN}✓ Đã có base_url và id_sach thủ công, tiếp tục...{RESET}")
                else:
                    print(f"{RED}❌ Cần link ebook để lấy base_url và id_sach{RESET}")
                    return
        else:
            print(f"{RED}❌ Không tìm thấy link ebook và số trang từ URL sách{RESET}")
            return
    else:
        if DEBUG_PROGRAM:
            print(f"{GREEN}✓ Link ebook: {ebook_link}{RESET}")

    if not id_sach and ebook_link:
        id_sach = get_id_sach_from_ebook_link(ebook_link, cookies)
        if id_sach:
            if DEBUG_PROGRAM:
                print(f"{GREEN}✓ id_sach: {id_sach}{RESET}")
        else:
            print(f"{RED}❌ Không tìm thấy id_sach{RESET}")

    if not base_url and ebook_link:
        base_url = get_base_url_from_ebook_link(ebook_link, cookies)
        if base_url:
            if DEBUG_PROGRAM:
                print(f"{GREEN}✓ base_url: {base_url}{RESET}")
        else:
            print(f"{RED}❌ Không tìm thấy base_url{RESET}")

    if not output_pdf or output_pdf.strip() == "" or output_pdf == "result.pdf":
        title = ebook_info.get("title")
        if title:
            if CONVERT_FILE_NAMES_TO_SLUG:
                pdf_name = slugify(title)
            else:
                pdf_name = re.sub(r'[<>:"/\\|?*]', "", title).strip()

                MAX_FILE_NAME = 200
                if len(pdf_name) > MAX_FILE_NAME:
                    pdf_name = pdf_name[:MAX_FILE_NAME]

            if pdf_name:
                output_pdf = f"{pdf_name}.pdf"
                if DEBUG_PROGRAM:
                    print(f"{GREEN}✓ Tên file PDF: {output_pdf}{RESET}")
            else:
                output_pdf = "result.pdf"
                if DEBUG_PROGRAM:
                    print(f"{YELLOW}⚠️  Không tạo được tên file từ title, sử dụng: {output_pdf}{RESET}")
        else:
            output_pdf = "result.pdf"
            if DEBUG_PROGRAM:
                print(f"{YELLOW}⚠️  Không lấy được title, sử dụng tên mặc định: {output_pdf}{RESET}")

    if DEBUG_PROGRAM:
        print(f"\n{CYAN}✅ Hoàn tất tự động lấy thông tin{RESET}\n")


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    return text


def main():
    validate_cookies()
    auto_fill_parameters()

    if not total_pages or total_pages == 0:
        print(f"{RED}❌ Lỗi: total_pages chưa được điền{RESET}")
        exit(1)

    if not base_url:
        print(f"{RED}❌ Lỗi: base_url chưa được điền{RESET}")
        exit(1)

    if not id_sach:
        print(f"{RED}❌ Lỗi: id_sach chưa được điền{RESET}")
        exit(1)

    cookie_header = "; ".join([GA, VISITOR, ANTIFORGERY, AUTH, GA_TRACK])

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://nxbbachkhoa.vn/",
        "Cookie": cookie_header,
    }

    print(f"{RED}Cảm ơn quý khách đã sử dụng dịch vụ tải xuống miễn phí không của Đại học Bách Khoa Hà Nội.{RESET}")
    print(f"{RED}Quý khách vui lòng chỉ sử dụng dịch vụ cho mục đích học tập và nghiên cứu.{RESET}")
    print(f"{RED}Mọi hành vi sử dụng với mục đích thương mại đều bị NGHIÊM CẤM.{RESET}")
    print(f"{RED}Tác giả và đơn vị triển khai tuyên bố miễn trừ mọi trách nhiệm phát sinh từ việc sử dụng trái quy định; người dùng tự chịu trách nhiệm trước PHÁP LUẬT về hành vi của mình.{RESET}")

    if MAKE_COLOR:

        crypto_print(
            f"🕒 Thời gian bắt đầu:  {__import__('datetime').datetime.now().strftime('%H:%M:%S')}",
            GREEN,
        )

    start_time = __import__("time").time()

    if DOWNLOAD_IMAGE:
        os.makedirs(save_dir, exist_ok=True)
        consecutive_failures = 0

        for i in range(1, total_pages + 1):
            file_name = f"{i}.jpg"
            url = f"{base_url}/{file_name}?{id_sach}"

            try:
                res = requests.get(url, headers=headers)
                if res.status_code == 200:
                    with open(os.path.join(save_dir, file_name), "wb") as f:
                        f.write(res.content)
                    if DEBUG_PROGRAM:
                        print(f"{GREEN}✔ Downloaded {file_name}{RESET}")
                    consecutive_failures = 0
                else:
                    consecutive_failures += 1
                    if DEBUG_PROGRAM:
                        print(f"{RED}❌ Failed (Status {res.status_code}): {file_name}{RESET}")

                    MAX_ERROR_ALLOWED = 5
                    if ENABLE_FAILED_IMAGE is False and consecutive_failures >= MAX_ERROR_ALLOWED:
                        if DEBUG_PROGRAM:
                            print(f"\n{YELLOW}⚠️  Phát hiện {MAX_ERROR_ALLOWED} ảnh lỗi liên tiếp{RESET}")
                            print(f"{YELLOW}⚠️  ENABLE_FAILED_IMAGE = False → Dừng download ảnh{RESET}")
                        break
            except Exception as e:
                consecutive_failures += 1
                if DEBUG_PROGRAM:
                    print(f"{RED}❌ Error downloading {file_name}: {e}{RESET}")
                if ENABLE_FAILED_IMAGE is False and consecutive_failures >= MAX_ERROR_ALLOWED:
                    if DEBUG_PROGRAM:
                        print(f"\n{YELLOW}⚠️  Phát hiện {consecutive_failures} ảnh lỗi liên tiếp{RESET}")
                        print(f"{YELLOW}⚠️  ENABLE_FAILED_IMAGE = False → Dừng download ảnh{RESET}")
                    break

        if DEBUG_PROGRAM:
            print(f"\n{CYAN}🎉 DONE — All images saved in /{save_dir}{RESET}")

    if MAKE_COLOR:
        crypto_print("⏳ Processing...", YELLOW)

    if SHOULD_MERGE_TO_PDF:
        if DEBUG_PROGRAM:
            print(f"\n{YELLOW}⏳ Merging images into PDF...{RESET}")

        files = sorted(
            [f for f in os.listdir(save_dir) if f.endswith(".jpg")],
            key=lambda x: int(x.split(".")[0]),
        )

        if not files:
            print(f"{RED}❌ Không có file ảnh nào để merge{RESET}")
        else:
            images = [Image.open(os.path.join(save_dir, f)).convert("RGB") for f in files]
            images[0].save(output_pdf, save_all=True, append_images=images[1:])

            if MAKE_COLOR:
                crypto_print("✅ Finishing...", GREEN)
            text = f"\n{GREEN}📌 PDF created successfully → {output_pdf}{RESET}"

            for char in text:
                sys.stdout.write(char)
                sys.stdout.flush()
                time.sleep(0.05)

            if MAKE_COLOR:
                end_time = __import__("time").time()
                duration = end_time - start_time
                crypto_print(
                    f"🕒 Thời gian kết thúc: {__import__('datetime').datetime.now().strftime('%H:%M:%S')}",
                    BLUE,
                    speed=0.02,
                    noise_level=10,
                )

                print()

                crypto_print(
                    f"⏱️  Thời gian xử lý: {duration:.2f} giây",
                    MAGENTA,
                    speed=0.02,
                    noise_level=10,
                )

                print("SUCCESSFULLY")

            if DEBUG_PROGRAM:
                print(f"{CYAN}🎉 DONE{RESET}")

            if DELETE_FOLDER_AFTER_MERGE:
                for f in files:
                    os.remove(os.path.join(save_dir, f))
                os.rmdir(save_dir)
                if DEBUG_PROGRAM:
                    print(f"{MAGENTA}🗑 Temporary folder '{save_dir}' deleted{RESET}")

    cleanup_temp_files()


if __name__ == "__main__":
    main()
