from html.parser import HTMLParser
import sys

class SyntaxChecker(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags_stack = []
        self.errors = []
        self.ignore_self_closing = ['meta', 'link', 'input', 'hr', 'img', 'br', 'source']

    def handle_starttag(self, tag, attrs):
        if tag not in self.ignore_self_closing:
            self.tags_stack.append((tag, self.getpos()))

    def handle_endtag(self, tag):
        if tag in self.ignore_self_closing:
            return
        if not self.tags_stack:
            self.errors.append(f"Mismatched closing tag </{tag}> at line {self.getpos()[0]}")
            return
        
        last_tag, pos = self.tags_stack.pop()
        if last_tag != tag:
            self.errors.append(f"Mismatched tags: opened <{last_tag}> at line {pos[0]} but closed with </{tag}> at line {self.getpos()[0]}")

def check_html():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    parser = SyntaxChecker()
    parser.feed(html_content)

    # Check unclosed tags
    if parser.tags_stack:
        for tag, pos in parser.tags_stack:
            parser.errors.append(f"Unclosed tag <{tag}> opened at line {pos[0]}")

    if parser.errors:
        print("HTML SYNTAX ERRORS FOUND:")
        for err in parser.errors:
            print("- " + err)
        sys.exit(1)
    else:
        print("SUCCESS: HTML structure is valid and all tags are matched.")

if __name__ == "__main__":
    check_html()
