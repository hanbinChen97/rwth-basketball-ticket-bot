1. Analysis Strategy (分析思路)
为了 automate the booking process，我们需要模拟浏览器点击 "Submit" 按钮的行为。

Locate the Row (定位行):

整个表格 class 是 bs_kurse。

我们需要找到包含目标 Kursnr (例如 13131817) 的那一行 <tr>。

在该行中，Kursnr 位于 <td class="bs_sknr"> 内。

Identify the Button (识别按钮):

在同一行中，找到 <td class="bs_sbuch"> (Booking column)。

Warteliste (现有逻辑): 这是一个 <input type="submit"> 标签。

关键属性是 name (例如 BS_Kursid_223188) 和 value (例如 Warteliste)。

Book (未来逻辑): 当时间到了，原本的 span (显示 "ab 30.11...") 会变成一个类似的 <input type="submit">，通常 value 会变成 "buchen" 或类似词，但最重要的是它的 name 属性（这是后端识别课程的唯一 ID）。

Construct Request (构造请求):

点击按钮本质上是发送一个 HTTP POST request。

Payload (Data): 必须包含该按钮的 name 和 value。

URL: 通常提交到当前页面的 URL (或 form 的 action URL)。


# 第一个页面点击
https://buchung.hsz.rwth-aachen.de/angebote/aktueller_zeitraum/_Basketball_Spielbetrieb.html?autoreload=1753005602101

1. 检查元素
<div class="bs_head" role="heading">Basketball Spielbetrieb</div>
确认页面是否正确。

2. soup 的 tbody 的 第三个 dr 的 第 9 个 tr 的 内容，是 button 的内容。
有可能是 “ab 03.12., 19:30” 这种没到时间的情况，有可能是 “wartlist” 的 button，也可能是 “buchen” button。