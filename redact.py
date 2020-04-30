from pathlib import Path
import nbformat

import const


def redact(p1, p2):
    """
    Redacts the textbook at p1 and write result as student book to p2
    Return a int error code when things going bad:
        0 - no error, 1 - unknown error, 2 - file error, etc.
    """
    try:
        source = nbformat.read(str(p1), as_version=nbformat.NO_CONVERT)
    except:
        return 2

    try:
        dest = {
            'cells': [],
            'metadata': source['metadata'],
            'nbformat': source['nbformat'],
            'nbformat_minor': source['nbformat_minor']
        }
        code_cell = {
            'cell_type': 'code',
            'metadata': {},
            'execution_count': 0,
            'outputs': [],
            'source': [const.SOURCE_PH]
        }

        for cell in source['cells']:
            if cell['cell_type'] == 'code':
                dest['cells'].append(code_cell)
            else:
                dest['cells'].append(cell)
    except:
        return 1

    try:
        nbformat.write(nbformat.from_dict(dest), str(p2), version=nbformat.NO_CONVERT)
        return 0
    except:
        return 2


if __name__ == '__main__':
    source = 'demo.ipynb'
    dest = 'redacted.ipynb'

    print(f"[INFO] processing {source}->{dest}")
    error = redact(Path(source), Path(dest))
    if error == 0:
        print('[INFO] succeeded')
    elif error == 2:
        print('[ERROR] file read/write failed')
    else:
        print('[ERROR] failed due to unknown error')