import os
import requests
from PIL import Image

###
# Tổng số trang của sách
total_pages = ""
download_images = True  # 🔥 đổi thành False nếu bạn đã có ảnh và chỉ muốn tạo PDF
merge_to_pdf = True  # 🔥 bật/tắt gộp PDF (merge image to pdf)
delete_folder_after_merge = True  # 🔥 bật/tắt xóa folder sau khi merge PDF xong

# Control shift I => Application => Cookies => https://nxbbachkhoa.vn/ => giữ nguyên tham số bên trái copy cột value ở phải dán vào nếu bị lỗi đăng nhập thôi
GA = ""
VISITOR = ""
ANTIFORGERY = ""
AUTH = ""
GA_TRACK = ""
cookie_header = "; ".join([GA, VISITOR, ANTIFORGERY, AUTH, GA_TRACK])

# Cách lấy base_url
# Làm bước 0 như ảnh buoc_0.png rồi xem video
base_url = ""
id_sach = ""

# Thư mục lưu tạm các image bạn tải
save_dir = "img"
# Tên pdf sau khi merge thành công
output_pdf = "result.pdf"
###

# Hết rồi đó phần dưới không sửa nha
headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://nxbbachkhoa.vn/",
    "Cookie": cookie_header,
}

# ===== ANSI COLORS =====
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
CYAN = "\033[36m"
MAGENTA = "\033[35m"
RESET = "\033[0m"

if download_images:
    os.makedirs(save_dir, exist_ok=True)
    for i in range(1, total_pages + 1):
        file_name = f"{i}.jpg"
        url = f"{base_url}/{file_name}?{id_sach}"

        try:
            res = requests.get(url, headers=headers)
            if res.status_code == 200:
                with open(os.path.join(save_dir, file_name), "wb") as f:
                    f.write(res.content)
                print(f"{GREEN}✔ Downloaded {file_name}{RESET}")
            else:
                print(f"{RED}❌ Failed (Status {res.status_code}): {file_name}{RESET}")
        except Exception as e:
            print(f"{RED}❌ Error downloading {file_name}: {e}{RESET}")

    print(f"\n{CYAN}🎉 DONE — All images saved in /{save_dir}{RESET}")

if merge_to_pdf:
    print(f"\n{YELLOW}⏳ Merging images into PDF...{RESET}")

    files = sorted(
        [f for f in os.listdir(save_dir) if f.endswith(".jpg")],
        key=lambda x: int(x.split(".")[0]),
    )

    images = [Image.open(os.path.join(save_dir, f)).convert("RGB") for f in files]
    images[0].save(output_pdf, save_all=True, append_images=images[1:])

    print(f"\n{GREEN}📌 PDF created successfully → {output_pdf}{RESET}")
    print(f"{CYAN}🎉 DONE{RESET}")

    if delete_folder_after_merge:
        for f in files:
            os.remove(os.path.join(save_dir, f))
        os.rmdir(save_dir)
        print(f"{MAGENTA}🗑 Temporary folder '{save_dir}' deleted{RESET}")
