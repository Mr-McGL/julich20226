#!/usr/bin/env python3
"""Check resources, reusable layouts and the text-only cover."""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAYOUTS = {'cover', 'text', 'split', 'sidebar', 'figure', 'results'}


def main() -> None:
    source = (ROOT / 'presentacion.md').read_text(encoding='utf-8')
    css = (ROOT / 'theme.css').read_text(encoding='utf-8')
    records = json.loads((ROOT / 'assets/videos/missing-videos.json').read_text(encoding='utf-8'))
    expected_missing = {record['replacement_path'] for record in records if record['status'] == 'missing'}
    references = set(re.findall(r'!\[[^\]]*\]\(([^\s)]+)', source))
    references.update(re.findall(r'\b(?:src|poster)="([^"]+)"', source))
    references.update(re.findall(r'url\([\'\"]?([^\'\")]+)', css))
    references.update(re.findall(r'url\([\'\"]?([^\'\")]+)', source))
    errors: list[str] = []
    missing_videos: list[str] = []
    for reference in sorted(references):
        if re.match(r'^(?:https?:|data:)', reference):
            continue
        if not (ROOT / reference).is_file():
            if reference in expected_missing:
                missing_videos.append(reference)
            else:
                errors.append(f'Missing local resource: {reference}')
    classes = re.findall(r'<!--\s*_class:\s*(.*?)\s*-->', source)
    if set(classes) - LAYOUTS:
        errors.append('Unknown slide layout found.')
    if re.search(r'^style:|<(?:style|svg)\b', source, re.M | re.I):
        errors.append('Embedded CSS or SVG found in the deck.')
    for tag, value in re.findall(r'<(\w+)\b[^>]*\bstyle="([^"]+)"', source):
        if tag != 'div' or any(not declaration.strip().startswith('--')
                               for declaration in value.split(';') if declaration.strip()):
            errors.append('Only local CSS variables on exceptional div elements are allowed.')
    if source.count('<div') != source.count('</div>'):
        errors.append('Unbalanced div elements.')
    header = re.match(r'\A---\s*\n.*?\n---\s*\n', source, re.S)
    slides = re.split(r'^---\s*$', source[header.end():], flags=re.M)
    if re.search(r'<div\b|!\[|<img\b|<video\b', slides[0]):
        errors.append('The cover must contain text only.')
    print(f'Slides: {len(slides)}')
    print(f'Shared layout types: {len(set(classes))}')
    print(f'Exceptional div elements: {source.count("<div")}')
    print(f'Local references checked: {len(references)}')
    for video in missing_videos:
        print(f'Expected missing original video: {video}')
    if errors:
        raise SystemExit('\n'.join(errors))
    print('Project checks passed.')


if __name__ == '__main__':
    main()
