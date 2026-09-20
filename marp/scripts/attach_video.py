#!/usr/bin/env python3
"""Attach a recovered MP4/WebM without changing the Markdown slide layout."""
from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def attach_video(slide: int, source_file: Path, shape_id: int | None = None) -> Path:
    """Copy a video into its slot and update only the matching src attribute."""
    source_file = source_file.expanduser().resolve()
    if not source_file.is_file():
        raise ValueError(f'Video file not found: {source_file}')
    extension = source_file.suffix.lower()
    if extension not in {'.mp4', '.webm'}:
        raise ValueError('Use an MP4 or WebM file. Convert AVI files first.')
    manifest_path = ROOT / 'assets/videos/missing-videos.json'
    records = json.loads(manifest_path.read_text(encoding='utf-8'))
    candidates = [record for record in records if record['slide'] == slide
                  and (shape_id is None or record['shape_id'] == shape_id)]
    if len(candidates) != 1:
        identifiers = ', '.join(str(record['shape_id']) for record in candidates)
        raise ValueError(f'Expected one video slot. Matching shape IDs: '
                         f'{identifiers or "none"}. Use --shape-id to disambiguate.')
    record = candidates[0]
    previous_path = record['replacement_path']
    relative_path = Path(previous_path).with_suffix(extension)
    target = (ROOT / relative_path).resolve()
    video_directory = (ROOT / 'assets/videos').resolve()
    if target.parent != video_directory:
        raise ValueError('The video destination must be inside assets/videos/.')
    deck_path = ROOT / 'presentacion.md'
    markdown = deck_path.read_text(encoding='utf-8')
    pattern = re.compile(r'(<video\b[^>]*\bsrc=)([\'\"])'
                         + re.escape(previous_path) + r'\2', re.I)
    revised, count = pattern.subn(
        lambda match: match.group(1) + match.group(2) + relative_path.as_posix() + match.group(2),
        markdown)
    if count != 1:
        raise ValueError(f'Expected one matching video tag, found {count}. '
                         'Check its src and the video manifest.')
    backup = deck_path.with_suffix('.md.bak')
    if not backup.exists():
        shutil.copy2(deck_path, backup)
    target.parent.mkdir(parents=True, exist_ok=True)
    if source_file != target:
        shutil.copy2(source_file, target)
    deck_path.write_text(revised, encoding='utf-8')
    record['status'] = 'attached_by_user'
    record['replacement_path'] = relative_path.as_posix()
    manifest_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--slide', type=int, required=True)
    parser.add_argument('--shape-id', type=int)
    parser.add_argument('--file', type=Path, required=True)
    parser.add_argument('--preview', action='store_true', help='Also rebuild the optional offline preview.')
    args = parser.parse_args()
    try:
        target = attach_video(args.slide, args.file, args.shape_id)
    except (OSError, ValueError, KeyError) as error:
        parser.error(str(error))
    print(f'Attached: {target}')
    if args.preview:
        try:
            from build_preview import build_preview
            print(f'Updated preview: {build_preview()}')
        except (OSError, ValueError, RuntimeError) as error:
            print(f'The video was attached, but the preview was not rebuilt: {error}')
    else:
        print('Regenerate any exported HTML after changing the video source.')


if __name__ == '__main__':
    main()
