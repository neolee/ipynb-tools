from pathlib import Path
import nbformat


def redact(p1, p2):
    '''redacts the notebook at source_fp and write result to dest_fp'''
    try:
        source = nbformat.read(str(p1), as_version=nbformat.NO_CONVERT)
    except Exception as e:
        print(f'[ERROR] cannot opening {p1}: {e}')
        return

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
        'source': ['# 请在这里输入代码']
    }

    for cell in source['cells']:
        if cell['cell_type'] == 'code':
            dest['cells'].append(code_cell)
        else:
            dest['cells'].append(cell)

    nbformat.write(nbformat.from_dict(dest), str(p2), version=nbformat.NO_CONVERT)


if __name__ == '__main__':
    redact(Path('demo.ipynb'), Path('redacted.ipynb'))