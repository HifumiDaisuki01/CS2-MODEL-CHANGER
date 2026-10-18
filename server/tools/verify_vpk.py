#!/usr/bin/env python3
"""Read a Valve VPK directory and validate every entry CRC; never mount or execute it."""
import argparse, pathlib, struct, zlib, json, hashlib

def inspect(path):
    path = pathlib.Path(path)
    with path.open('rb') as source:
        signature, version, size = struct.unpack('<III', source.read(12))
    if signature != 0x55AA1234 or version not in (1, 2):
        raise ValueError('Unsupported VPK signature/version')
    header = 12 if version == 1 else 28
    if size > 64 * 1024 * 1024: raise ValueError('VPK directory tree exceeds 64 MiB')
    with path.open('rb') as source: data=source.read(header+size)
    pos, end = header, header + size
    if end > len(data): raise ValueError('Truncated directory')
    def word():
        nonlocal pos
        stop = data.index(b'\0', pos, end)
        value = data[pos:stop].decode('utf-8'); pos = stop + 1
        return value
    entries = []
    archives = {}
    while (ext := word()):
        while (folder := word()):
            while (name := word()):
                crc, preload, archive, offset, length, terminator = struct.unpack_from('<IHHIIH', data, pos)
                pos += 18
                if terminator != 0xFFFF: raise ValueError('Invalid entry terminator')
                prefix = data[pos:pos + preload]; pos += preload
                if pos > end: raise ValueError('Truncated preload')
                if archive == 0x7FFF:
                    chunk, start = path, end + offset
                else:
                    if archive not in archives:
                        chunk = path.with_name(path.name.removesuffix('_dir.vpk') + f'_{archive:03d}.vpk')
                        archives[archive] = chunk
                    chunk, start = archives[archive], offset
                digest=hashlib.sha256(prefix); actual=zlib.crc32(prefix); remaining=length
                with chunk.open('rb') as source:
                    source.seek(start)
                    while remaining:
                        block=source.read(min(remaining,1024*1024))
                        if not block: raise ValueError('Truncated VPK payload')
                        digest.update(block); actual=zlib.crc32(block,actual); remaining-=len(block)
                if actual != crc:
                    raise ValueError('CRC/length mismatch: ' + name)
                resource = ('' if folder == ' ' else folder + '/') + name + '.' + ext
                if pathlib.PurePosixPath(resource).is_absolute() or '..' in pathlib.PurePosixPath(resource).parts:
                    raise ValueError('Unsafe resource path')
                entries.append(dict(Path=resource, Bytes=preload+length, SHA256=digest.hexdigest(), CRC32=f'{crc:08x}'))
    if pos != end: raise ValueError('Unexpected trailing tree bytes')
    def file_hash(p):
        digest=hashlib.sha256()
        with p.open('rb') as source:
            while block:=source.read(1024*1024):digest.update(block)
        return digest.hexdigest()
    return dict(Vpk=str(path), Version=version, Entries=entries, AllEntryCRCsValid=True,
                ArchiveSHA256={str(p):file_hash(p) for p in {path,*archives.values()}})

if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('vpk');parser.add_argument('--output');args=parser.parse_args()
    result=inspect(args.vpk);text=json.dumps(result,indent=2)
    if args.output:pathlib.Path(args.output).write_text(text+'\n')
    else:print(text)
