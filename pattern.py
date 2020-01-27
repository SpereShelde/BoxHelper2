import re

def check_html():
    raw = None
    try:
        f = open('pattern.html')
        raw = f.read()
        f.close()
    except IOError:
        print("Cannot load 'pattern.html'. Maybe it not exist.")
    if not raw:
        print("Cannot load 'pattern.html'. Maybe it's empty.")
        return None
    return raw


def find_detail():
    raw = check_html()
    if not raw:
        return
    print("Completed loading 'pattern.html'.")
    print("Please input detail link: ", end='')
    detail_link = input().strip()
    while not detail_link:
        print("Please input detail link: ", end='')
        detail_link = input().strip()
    print("########## BoxHelper - start ##########")
    pattern = None
    if detail_link in raw:
        start = raw.index(detail_link)-1
        end = start + len(detail_link)+1
        pattern = "%s(.*?)%s[^>]*?>" % (raw[start], raw[end])
        start -= 1
        while start >= 0 and raw[start] != " ":
            pattern = raw[start] + pattern
            start -= 1
        reg = re.compile('\S*')
        strs = reg.findall(raw[start - 200:start])
        for i in reversed(range(len(strs))):
            s = strs[i]
            while '<' in s:
                pattern = "%s[^<]*?%s" % (s[s.rindex('<'):], pattern)
                s = s[:s.rindex('<')]
    if pattern:
        reg = re.compile(pattern)
        similars = find_similar(raw, reg)
        print("BoxHelper found %d similar detail links based on '%s':" % (len(similars), detail_link))
        for similar in similars:
            print(similar)
    print("########## BoxHelper - end ############")
    print("If they are correct, please copy the pattern below and fill in the config.ini:\n")
    print(pattern)


def find_similar(str, reg):
    regex = re.compile(reg)
    res = regex.search(str)
    similars = []
    while res is not None:
        end = res.end()
        similars.append(res.group(1))
        str = str[end:]
        res = regex.search(str)
    return similars

find_detail()
