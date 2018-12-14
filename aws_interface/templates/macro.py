
import re

import os

def search(dirname, extension):
    filenames = os.listdir(dirname)
    for filename in filenames:
        full_filename = os.path.join(dirname, filename)
        ext = os.path.splitext(full_filename)[-1]
        if ext == extension:
            yield full_filename


if __name__ == '__main__':
    static_pattern = re.compile('.*assets.+')
    root_path = 'dashboard'
    ext = '.html'
    prefix = '{% static '
    postfix = ' %}'
    htmls = search(root_path, ext)
    for html_name in htmls:
        f = open(html_name, 'r')
        lines = f.readlines()
        reg = re.compile('"[a-zA-Z.][^"]+\/[^"]*"')

        new_html = "{% load staticfiles %}\n"

        for line in lines:
            if prefix not in line:
                ms = reg.findall(line)
                for m in ms:
                    if static_pattern.match(m):
                        repl = prefix + m + postfix
                        line = line.replace(m, repl)
                        print(line)
            new_html += line
        f.close()
        f = open(html_name + '.new.html', 'w+')
        f.write(new_html)
        f.close()
