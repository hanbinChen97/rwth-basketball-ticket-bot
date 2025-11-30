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

