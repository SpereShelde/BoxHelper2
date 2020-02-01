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
    print("Please input detail link: ", end='')
    detail_link = input().strip()
    while not detail_link:
        print("Please input detail link: ", end='')
        detail_link = input().strip()
    print("########## BoxHelper - start ##########")
    pattern = None
    if '"%s"'%detail_link in raw:
        start = raw.index(detail_link)-1
        end = start + len(detail_link)+1
        next_index = raw[end:].index('>')
        pre_index = raw[:start].rindex('<')
        pattern = '<[^<>]*?href="(?P<link>%s[^"]*)"[^<>]*?>' % detail_link[:3]
        # if 'title="' in raw[end:next_index]:
        #     pattern = '<[^<>]*?href="(?P<link>%s[^"]*)"[^<>]*?title="(?P<title>[^"]*)"[^>]*?>' % detail_link[:3]
        #     # pattern = '%s(.*?)%s[^>]*?title="(.*?)"[^>]*?>' % (raw[start], raw[end])
        # else:
        #     pattern = '<[^<>]*?title="(?P<title>[^"]*)"[^<>]*?href="(?P<link>%s[^"]*)"[^>]*?>' % detail_link[:3]
            # pattern = '%s(.*?)%s[^>]*?>' % (raw[start], raw[end])

        reg = re.compile('\S+')
        strs = reg.findall(raw[pre_index - 100:pre_index])
        for i in reversed(range(len(strs))):
            s = strs[i]
            while '<' in s:
                pattern = '%s[^<]*?%s' % (s[s.rindex('<'):], pattern)
                s = s[:s.rindex('<')]
    if pattern:
        # print(pattern)
        reg = re.compile(pattern)
        results = find_group(raw, reg)
        print("BoxHelper found %d similar detail links based on '%s':" % (len(results), detail_link))
        # for result in results:
        #     if '' in result:
        #         continue
        #     for r in result:
        #         print(r)
        for res in results:
            print(res)

    print("########## BoxHelper - end ############")
    return pattern




def find_group(str, reg):
    regex = re.compile(reg)
    res = regex.search(str)
    # results = [[],[]]
    results = []
    while res is not None:
        # results[0].append(res.group('title'))
        # results[1].append(res.group('link'))
        results.append(res.group('link'))
        str = str[res.end():]
        res = regex.search(str)
    return results

def check_input(output):
    print(output, end='')
    correct = input().strip()
    if correct.capitalize() == "Y" or correct.capitalize() == "YES":
        return True
    elif correct.capitalize() == "N" or correct.capitalize() == "NO":
        return False
    else:
        return check_input(output)

def check():
    pattern_list = []
    pattern = find_detail()
    while True:
        inp = check_input("Are they completely correct? (Y/n): ")
        if not inp:
            inp = check_input("Need another try? (Y/n): ")
            if inp:
                pattern = find_detail()
                continue
            else:
                inp = check_input("Save previous results? (Y/n): ")
                if inp:
                    print('@Box#Helper@'.join(pattern_list))
                    return
                else:
                    print("Cannot find all correct detail link, please contact author.")
                    return
        else:
            pattern_list.append(pattern)
            inp = check_input("Any other patterns need to find? (Y/n): ")
            if inp:
                pattern = find_detail()
            else:
                print("Please check the pattern:")
                print('@Box#Helper@'.join(pattern_list))
                return

if __name__ == '__main__':
    raw = check_html()
    if raw:
        print("Completed loading 'pattern.html'.")
        check()
