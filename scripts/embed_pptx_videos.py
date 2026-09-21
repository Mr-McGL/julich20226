#!/usr/bin/env python3
"""Embed local MP4 videos in a Marp PPTX (standard library + FFmpeg only).

Supports this project's sidebar/split/figure layouts and .media divs.
Reads their pixel coordinates from theme.css and Markdown; no slide numbers
or video filenames are hard-coded. Export the PPTX again after editing slides.
"""
from __future__ import annotations

import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
NS = {
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'p14': 'http://schemas.microsoft.com/office/powerpoint/2010/main',
}
for prefix, uri in NS.items():
    ET.register_namespace(prefix, uri)
REL = 'http://schemas.openxmlformats.org/package/2006/relationships'
CT = 'http://schemas.openxmlformats.org/package/2006/content-types'


def node(parent, tag, **attrs):
    prefix, name = tag.split(':')
    return ET.SubElement(parent, f'{{{NS[prefix]}}}{name}', {
        (f'{{{NS[k.split(":")[0]]}}}{k.split(":")[1]}' if ':' in k else k): str(v)
        for k, v in attrs.items()})


def xml(element):
    return ET.tostring(element, encoding='utf-8', xml_declaration=True)


class Attributes(HTMLParser):
    def handle_starttag(self, tag, attrs):
        self.attrs = dict(attrs)


def attributes(tag):
    parser = Attributes()
    parser.feed(tag)
    return parser.attrs


def declarations(text):
    return dict(re.findall(r'([\w-]+)\s*:\s*([^;{}]+)', text))


def pixels(value):
    if not re.fullmatch(r'-?[\d.]+px', value.strip()):
        raise ValueError(f'Expected a pixel coordinate, got {value!r}')
    return float(value.strip()[:-2])


def rule(css, selector):
    match = re.search(re.escape(selector) + r'\s*\{([^}]+)\}', css)
    if not match:
        raise ValueError(f'Unsupported theme: missing {selector}')
    return declarations(match[1])


def video_slots(source, theme):
    text = source.read_text(encoding='utf-8')
    text = re.sub(r'\A---\s*\n.*?\n---\s*\n', '', text, count=1, flags=re.S)
    # Comments may themselves contain slide separators.
    text = re.sub(r'<!--(?!\s*_class:).*?-->', '', text, flags=re.S)
    slides = re.split(r'^---\s*$', text, flags=re.M)
    css = re.sub(r'/\*.*?\*/', '', theme.read_text(encoding='utf-8'), flags=re.S)
    size = rule(css, 'section')
    dimensions = (pixels(size['width']), pixels(size['height']))
    slots = []
    for number, slide in enumerate(slides, 1):
        layout = re.search(r'<!--\s*_class:\s*(\w+)\s*-->', slide)
        layout = layout[1] if layout else ''
        stack, media_index = [], 0
        tokens = re.finditer(r'<div\b[^>]*>|</div\s*>|<video\b[^>]*>|<img\b[^>]*>|!\[[^\]]*\]\([^\n]+?\)', slide)
        for token in tokens:
            tag = token[0]
            if tag.startswith('<div'):
                stack.append(attributes(tag))
                continue
            if tag.startswith('</div'):
                stack.pop()
                continue
            index = media_index
            if not stack:
                media_index += 1
            if not tag.startswith('<video'):
                continue
            attrs = attributes(tag)
            if stack:
                if len(stack) != 1 or 'media' not in stack[-1].get('class', '').split():
                    raise ValueError(f'Slide {number}: unsupported video container')
                values = declarations(stack[-1].get('style', ''))
                if any(key.startswith('--image-') for key in values):
                    raise ValueError('Cropped videos are not supported')
                box = [pixels(values[key]) for key in ('--x', '--y', '--w', '--h')]
                contain = False
            else:
                if layout not in {'sidebar', 'split', 'figure'}:
                    raise ValueError(f'Slide {number}: unsupported video layout {layout!r}')
                selector = f'section.{layout} > :is(p:has(> img, > video), video)'
                values = rule(css, selector)
                if layout == 'sidebar':
                    if index > 3:
                        raise ValueError('Sidebar supports at most four media slots')
                    if index % 2:
                        values.update(rule(css, 'section.sidebar > :nth-child(2n of p:has(> img, > video), video)'))
                    if index >= 2:
                        values.update(rule(css, 'section.sidebar > :nth-child(n+3 of p:has(> img, > video), video)'))
                box = [pixels(values[key]) for key in ('left', 'top', 'width', 'height')]
                contain = True
            url = urlsplit(attrs.get('src', ''))
            if url.scheme or url.netloc or not url.path:
                raise ValueError('Videos must use local paths in their src attribute')
            path = (source.parent / unquote(url.path)).resolve()
            if path.suffix.lower() != '.mp4' or not path.is_file():
                raise ValueError(f'Missing local MP4: {path}')
            slots.append((number, path, box, contain))
    return len(slides), dimensions, slots


def embed(source, theme, pptx, output):
    if pptx.resolve() == output.resolve():
        raise ValueError('Use a different output path to preserve the original PPTX')
    for command in ('ffmpeg', 'ffprobe'):
        if not shutil.which(command):
            raise ValueError(f'{command} is required; install FFmpeg first')
    count, (width, height), slots = video_slots(source, theme)
    if not slots:
        raise ValueError('No videos found in Markdown')
    with ZipFile(pptx) as archive, tempfile.TemporaryDirectory() as work:
        presentation = ET.fromstring(archive.read('ppt/presentation.xml'))
        if len(presentation.find('p:sldIdLst', NS)) != count:
            raise ValueError('Slide count differs: export the current Markdown to PPTX first')
        if any(n.startswith('ppt/media/codex-video-') for n in archive.namelist()):
            raise ValueError('This PPTX already contains embedded videos; use the original Marp export')
        size = presentation.find('p:sldSz', NS)
        sx, sy = int(size.get('cx')) / width, int(size.get('cy')) / height
        if abs(sx / sy - 1) > .001:
            raise ValueError('PPTX aspect ratio does not match the theme')
        updated, additions, trees = {}, {}, {}
        types = ET.fromstring(archive.read('[Content_Types].xml'))
        for ext, mime in [('mp4', 'video/mp4'), ('png', 'image/png')]:
            if not any(e.get('Extension') == ext for e in types):
                ET.SubElement(types, f'{{{CT}}}Default', Extension=ext, ContentType=mime)
        for ordinal, (number, path, box, contain) in enumerate(slots, 1):
            slide_name = f'ppt/slides/slide{number}.xml'
            rel_name = f'ppt/slides/_rels/slide{number}.xml.rels'
            if number not in trees:
                slide = ET.fromstring(archive.read(slide_name))
                if slide.find('p:timing', NS) is not None:
                    raise ValueError('Expected a fresh Marp export without animation timing')
                rels = ET.fromstring(archive.read(rel_name))
                trees[number] = slide, rels
            slide, rels = trees[number]
            streams = json.loads(subprocess.check_output([
                'ffprobe', '-v', 'error', '-show_streams', '-of', 'json', str(path)]))['streams']
            video = next(s for s in streams if s['codec_type'] == 'video')
            if video['codec_name'] != 'h264' or any(s['codec_name'] != 'aac' for s in streams if s['codec_type'] == 'audio'):
                raise ValueError(f'{path.name}: convert to H.264/AAC for PowerPoint first')
            stem = f'codex-video-{ordinal}'
            poster = Path(work) / f'{stem}.png'
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(path),
                            '-frames:v', '1', '-update', '1', str(poster)], check=True)
            additions[f'ppt/media/{stem}.mp4'] = path
            additions[f'ppt/media/{stem}.png'] = poster
            ids = []
            for kind, suffix in [('video', 'mp4'), ('media', 'mp4'), ('image', 'png')]:
                rid = f'rIdCodexVideo{ordinal}{kind}'
                ids.append(rid)
                uri = NS['r'] + '/' + kind if kind != 'media' else 'http://schemas.microsoft.com/office/2007/relationships/media'
                ET.SubElement(rels, f'{{{REL}}}Relationship', Id=rid, Type=uri, Target=f'../media/{stem}.{suffix}')
            tree = slide.find('p:cSld/p:spTree', NS)
            shape_id = max(int(e.get('id')) for e in tree.findall('.//p:cNvPr', NS)) + 1
            x, y, w, h = box
            # Cover the flattened HTML poster/controls before adding the movie.
            if contain:
                bg = node(tree, 'p:sp')
                nv = node(bg, 'p:nvSpPr')
                node(nv, 'p:cNvPr', id=shape_id, name=f'Video background {ordinal}')
                node(nv, 'p:cNvSpPr'); node(nv, 'p:nvPr')
                sp = node(bg, 'p:spPr')
                transform(sp, x, y, w, h, sx, sy)
                node(node(sp, 'a:solidFill'), 'a:srgbClr', val='FFFFFF')
                node(node(sp, 'a:ln'), 'a:noFill')
                shape_id += 1
                scale = min(w / video['width'], h / video['height'])
                vw, vh = video['width'] * scale, video['height'] * scale
                x, y, w, h = x + (w-vw)/2, y + (h-vh)/2, vw, vh
            picture = node(tree, 'p:pic')
            nv = node(picture, 'p:nvPicPr')
            props = node(nv, 'p:cNvPr', id=shape_id, name=path.name)
            node(props, 'a:hlinkClick', **{'r:id': '', 'action': 'ppaction://media'})
            node(node(nv, 'p:cNvPicPr'), 'a:picLocks', noChangeAspect='1')
            nvpr = node(nv, 'p:nvPr')
            node(nvpr, 'a:videoFile', **{'r:link': ids[0]})
            ext = node(node(nvpr, 'p:extLst'), 'p:ext', uri='{DAA4B4D4-6D71-4841-9C94-3DE7FCFB9230}')
            node(ext, 'p14:media', **{'r:embed': ids[1]})
            fill = node(picture, 'p:blipFill')
            node(fill, 'a:blip', **{'r:embed': ids[2]})
            node(node(fill, 'a:stretch'), 'a:fillRect')
            transform(node(picture, 'p:spPr'), x, y, w, h, sx, sy)
            timing = slide.find('p:timing', NS)
            if timing is None:
                timing = node(slide, 'p:timing')
                root = node(node(node(timing, 'p:tnLst'), 'p:par'), 'p:cTn', id=1, dur='indefinite', restart='never', nodeType='tmRoot')
                node(root, 'p:childTnLst')
            children = timing.find('.//p:childTnLst', NS)
            media = node(node(children, 'p:video'), 'p:cMediaNode', vol=80000)
            ct = node(media, 'p:cTn', id=ordinal+1, fill='hold', display=0)
            node(node(ct, 'p:stCondLst'), 'p:cond', delay='indefinite')
            node(node(media, 'p:tgtEl'), 'p:spTgt', spid=shape_id)
            updated[slide_name], updated[rel_name] = xml(slide), xml(rels)
            print(f'Diapositiva {number}: {path.name}')
        updated['[Content_Types].xml'] = xml(types)
        # Write atomically; errors never leave a partial destination file.
        with tempfile.NamedTemporaryFile(dir=output.parent, suffix='.pptx', delete=False) as tmp:
            temporary = Path(tmp.name)
        try:
            with ZipFile(temporary, 'w', ZIP_DEFLATED) as result:
                for item in archive.infolist():
                    result.writestr(item, updated.get(item.filename, archive.read(item.filename)))
                for name, path in additions.items():
                    result.write(path, name)
            temporary.replace(output)
        finally:
            temporary.unlink(missing_ok=True)
    print(f'{len(slots)} vídeos incrustados: {output}')


def transform(parent, x, y, w, h, sx, sy):
    xf = node(parent, 'a:xfrm')
    node(xf, 'a:off', x=round(x*sx), y=round(y*sy))
    node(xf, 'a:ext', cx=round(w*sx), cy=round(h*sy))
    node(node(parent, 'a:prstGeom', prst='rect'), 'a:avLst')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT / 'presentacion.md')
    parser.add_argument('--theme', type=Path, default=ROOT / 'theme.css')
    parser.add_argument('--input', type=Path, default=ROOT / 'presentacion.pptx')
    parser.add_argument('--output', type=Path, default=ROOT / 'presentacion-con-videos.pptx')
    args = parser.parse_args()
    try:
        embed(args.source, args.theme, args.input, args.output)
    except (ValueError, OSError, KeyError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'Error: {error}\n')


if __name__ == '__main__':
    main()
