import re

with open('test_login_ui.js', 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace('const page = await browser.newPage();', 'const page = await browser.newPage();\n    page.on("console", msg => console.log("PAGE LOG:", msg.text()));')

with open('test_login_ui.js', 'w', encoding='utf-8') as f:
    f.write(c)
