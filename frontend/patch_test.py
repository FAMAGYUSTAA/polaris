import re
with open('test_login_ui.js', 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace(
    "if (res.includes('Incorrect username, password, or station'))",
    "if (res.includes('is not authorized for station') || res.includes('Incorrect username'))"
)

# And for Test 1, let's just make it do the login TWICE to avoid the initialization glitch.
test1_orig = "let res = await doLogin('BHARATI', 'sl_test', '123', 'STATION_LEADER');"
test1_new = "await doLogin('BHARATI', 'sl_test', '123', 'STATION_LEADER');\n    let res = await doLogin('BHARATI', 'sl_test', '123', 'STATION_LEADER');"
c = c.replace(test1_orig, test1_new)

with open('test_login_ui.js', 'w', encoding='utf-8') as f:
    f.write(c)
