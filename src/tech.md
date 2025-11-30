# process_booking
1. httpx 访问 target web site。
2. 如果有 “buchen” button，点击。
3. 会 popup 一个新窗口。
4. 这个新窗口中，点击 “buchen” button。
5. 再当前窗口中，会跳转内容，到新页面，用来填表。
6. 填写表单，点击 “buchen” button。
7. 当前页面会，跳转到新内容，还有再点击 “buchen”
8. 完成。
这个程序可以，单次运行，完成 booking。
目前，代码的还不完善，我没确认，按钮的名称，是否是固定的，form 的 name 是否是固定的。
所有，请你先不要写死，像是一个 placeholder。 等我看到每个步骤的 html 内容，再确认。


# main
loop， check the content of website， if found the booking info，call process_booking。
比如 19:00 开放，我会提前几分钟运行程序，每个 500ms 检查一次。
这是一个自动化程序。

# 代码有两个entry point。


# page 1
[page 1 html](../data/page1.html)这里是针对**唯一可用按钮**的自动化代码。

逻辑很简单：

1.  抓取 `form` 的 `action` URL。
2.  抓取隐藏的 `fid`。
3.  抓取**唯一**的 `class="buchen"` 按钮的 `name`。
4.  组合数据并 **POST**。

### Python Code (httpx + bs4)

```python
import httpx
from bs4 import BeautifulSoup

# 假设你已经获取了页面内容，存为 html_content
# html_content = client.get("PAGE_URL").text 

def submit_booking(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # 1. 获取 Form Action URL & Hidden FID
    form = soup.find('form', attrs={'name': 'bsform'})
    post_url = form['action']  # https://buchung.hsz.rwth-aachen.de/cgi/anmeldung.fcgi
    fid = soup.find('input', attrs={'name': 'fid'})['value']

    # 2. 找到唯一的 "buchen" 按钮
    # 既然只有一个，直接用 find 找 class 为 "buchen" 的 input
    btn = soup.find('input', attrs={'class': 'buchen', 'type': 'submit'})

    if not btn:
        print("❌ Error: No booking button found!")
        return None

    # 3. 构造 Payload (Form Data)
    # 关键：把按钮的 name 作为 key 发送，模拟点击行为
    payload = {
        'fid': fid,
        btn['name']: btn['value'] # e.g., 'BS_Termin_2025-12-01': 'buchen'
    }

    # 4. 发送请求 (Submit)
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        # 最好带上 Referer，防止服务器校验
        "Referer": "https://buchung.hsz.rwth-aachen.de/" 
    }

    print(f"🚀 Submitting for: {btn['name']}...")
    
    with httpx.Client() as client:
        response = client.post(post_url, data=payload, headers=headers)

    # 5. 检查结果
    if response.status_code == 200:
        print("✅ Success! Moved to next page.")
        # 返回下一页的 HTML，通常是填写个人信息的表单
        return response.text
    else:
        print(f"❌ Failed. Status: {response.status_code}")
        return None

# 使用示例
# next_page_html = submit_booking(your_html_string)
```