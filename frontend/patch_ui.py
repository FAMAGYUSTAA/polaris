import re

with open('test_login_ui.js', 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace('console.log("  [FAIL]");', 'console.log("  [FAIL] \\n" + res.substring(0, 100));')

with open('test_login_ui.js', 'w', encoding='utf-8') as f:
    f.write(c)
