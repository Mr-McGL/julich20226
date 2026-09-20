#!/usr/bin/env python3
"""Build an offline layout preview using CommonMark and the external theme.

This optional helper is not Marp CLI. Use the VS Code Marp extension or
`npm run html` for native Marp output and its presenter features.
"""
from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build_preview(source: Path | None = None, output: Path | None = None) -> Path:
    """Render the deck, preserving its local assets, layout classes and notes."""
    try:
        import yaml
        from markdown_it import MarkdownIt
    except ImportError as error:
        raise RuntimeError(
            'Install the optional preview dependencies: '
            'python -m pip install -r scripts/requirements-preview.txt'
        ) from error
    source = source or ROOT / 'presentacion.md'
    output = output or ROOT / 'vista_previa.html'
    text = source.read_text(encoding='utf-8')
    header = re.match(r'\A---\s*\n(.*?)\n---\s*\n', text, re.S)
    settings = yaml.safe_load(header.group(1)) if header else {}
    body = text[header.end():] if header else text
    slides = re.split(r'^---\s*$', body, flags=re.M)
    parser = MarkdownIt('commonmark', {'html': True})
    sections: list[str] = []
    notes: list[str] = []
    for number, slide in enumerate(slides, 1):
        directives: dict[str, str] = {}
        slide_notes: list[str] = []
        for comment in re.findall(r'<!--(.*?)-->', slide, re.S):
            match = re.fullmatch(r'\s*(_\w+)\s*:\s*(.*?)\s*', comment, re.S)
            if match:
                directives[match.group(1)] = str(yaml.safe_load(match.group(2)))
            else:
                slide_notes.append(comment.strip())
        content = parser.render(re.sub(r'<!--.*?-->', '', slide, flags=re.S))
        if '_footer' in directives:
            content += '<footer>' + parser.renderInline(directives['_footer']) + '</footer>'
        class_name = html.escape(directives.get('_class', ''), quote=True)
        background = directives.get('_backgroundImage', '')
        style = ' style="background-image: ' + html.escape(background, quote=True) + '"' if background else ''
        sections.append(f'<section class="{class_name}"{style} data-slide="{number}" '
                        f'aria-label="Slide {number}">{content}</section>')
        notes.append('\n\n'.join(slide_notes))
    css = settings.get('style') or (ROOT / 'theme.css').read_text(encoding='utf-8')
    css = re.sub(r'@import\s+[\'"]default[\'"];', '', css)
    template = (ROOT / 'scripts/preview-template.html').read_text(encoding='utf-8')
    replacements = {
        '{{TITLE}}': html.escape(settings.get('title', 'VG-LAB')),
        '{{THEME}}': css,
        '{{SLIDES}}': '\n'.join(sections),
        '{{NOTES}}': json.dumps(notes, ensure_ascii=False).replace('</', '<\\/'),
    }
    for token, value in replacements.items():
        template = template.replace(token, value)
    output.write_text(template, encoding='utf-8')
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        print(build_preview(args.source, args.output))
    except (OSError, ValueError, RuntimeError) as error:
        parser.error(str(error))


if __name__ == '__main__':
    main()
