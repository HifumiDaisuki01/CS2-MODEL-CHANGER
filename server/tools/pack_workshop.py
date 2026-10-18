#!/usr/bin/env python3
"""Build an unsigned VPK v2 resource addon, preserving every input byte/path.

Usage: python3 pack_workshop.py RESOURCE_ROOT OUTPUT_DIR
OUTPUT_DIR must be new. Produces pak01_dir.vpk and pak01_000.vpk.
No Steam upload, model compilation, or server configuration is performed.
"""
import hashlib, pathlib, struct, sys, zlib

def pack(root, output):
    root, output = pathlib.Path(root).resolve(), pathlib.Path(output).resolve()
    if output == root or output.is_relative_to(root):
        raise ValueError('Output must be outside input resources')
    if output.exists(): raise FileExistsError('Use a new output directory')
    files = sorted(p for p in root.rglob('*') if p.is_file())
    if not files: raise ValueError('No resources')
    groups, seen, payload = {}, set(), bytearray()
    for p in files:
        name = p.relative_to(root).as_posix()
        if p.is_symlink() or not p.resolve().is_relative_to(root): raise ValueError('Unsafe input')
        if name.lower() in seen or '\\' in name or '\0' in name: raise ValueError('Path collision')
        seen.add(name.lower())
        folder, leaf = name.rsplit('/', 1) if '/' in name else (' ', name)
        stem, ext = leaf.rsplit('.', 1) if '.' in leaf else (leaf, ' ')
        data = p.read_bytes(); offset = len(payload); payload.extend(data)
        if len(payload) >= 0xffffffff: raise ValueError('Single chunk limit exceeded')
        entry = struct.pack('<IHHIIH', zlib.crc32(data), 0, 0, offset, len(data), 0xffff)
        groups.setdefault(ext, {}).setdefault(folder, []).append((stem, entry))
    tree = bytearray()
    def word(s): tree.extend(s.encode('utf-8') + b'\0')
    for ext, folders in sorted(groups.items()):
        word(ext)
        for folder, entries in sorted(folders.items()):
            word(folder)
            for stem, entry in sorted(entries): word(stem); tree.extend(entry)
            word('')
        word('')
    word('')
    md5s = bytearray()
    for offset in range(0, len(payload), 1024*1024):
        block = payload[offset:offset+1024*1024]
        md5s.extend(struct.pack('<III16s', 0, offset, len(block), hashlib.md5(block).digest()))
    header = struct.pack('<7I', 0x55aa1234, 2, len(tree), 0, len(md5s), 48, 0)
    prefix = header + tree + md5s + hashlib.md5(tree).digest() + hashlib.md5(md5s).digest()
    directory = prefix + hashlib.md5(prefix).digest()
    output.mkdir(parents=True)
    (output/'pak01_000.vpk').write_bytes(payload)
    (output/'pak01_dir.vpk').write_bytes(directory)
    return len(files), len(payload), len(directory)

if __name__ == '__main__':
    print('Packed files / payload bytes / directory bytes:', *pack(*sys.argv[1:]))
