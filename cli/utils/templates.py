import re


def normalize_body(content: str, project_name: str) -> str:
    m = re.match(r'^(---\n.*?\n---\n)', content, re.DOTALL)
    if m:
        header = m.group(1)
        body = content[m.end():]
    else:
        header, body = '', content

    body = re.sub(r'/(?:Users|home)/\S+', '<path>', body)
    if project_name:
        body = body.replace(project_name, '<project-name>')

    return header + body
