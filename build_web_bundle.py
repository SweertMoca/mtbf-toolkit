"""Rebuild bundle from existing literal FILES and root Markdown. No network."""
import ast
import hashlib
import json
from pathlib import Path


def main():
    root = Path(__file__).resolve().parent
    target = root / 'COPY_THIS_bootstrap.py'
    source = target.read_text(encoding='utf-8-sig')
    tree = ast.parse(source)
    assignments = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            assignments[node.targets[0].id] = node
    files_node, hashes_node = assignments['FILES'], assignments['SHA256']
    files = ast.literal_eval(files_node.value)
    for name in list(files) + ['AA_PC_FIRST_RUN.md', 'IMPLEMENTATION_STATUS.md']:
        path = root / name
        if name.endswith('.md') and path.is_file():
            files[name] = path.read_text(encoding='utf-8-sig')
    hashes = {name: hashlib.sha256(content.encode('utf-8')).hexdigest() for name, content in files.items()}
    lines = source.splitlines(keepends=True)
    edits = [(files_node, 'FILES = ' + json.dumps(files, ensure_ascii=False, indent=2) + '\n'),
             (hashes_node, 'SHA256 = ' + json.dumps(hashes, indent=2) + '\n')]
    for node, replacement in sorted(edits, key=lambda item: item[0].lineno, reverse=True):
        lines[node.lineno-1:node.end_lineno] = [replacement]
    output = ''.join(lines)
    ast.parse(output)
    with target.open('w', encoding='utf-8', newline='\n') as stream:
        stream.write(output)
    print('Rebuilt bundle with', len(files), 'files. Restore in a NEW directory and test before publishing.')


if __name__ == '__main__':
    main()
