from pathlib import Path
import nbformat

import const


def check_cell(cell1, cell2):
    """
    Check one cell of completed student book (cell2) with original ones (cell1)
    Return an int number as result: 
        0 = failed, i.e. empty or not run with error
        1 = worked, i.e. not empty and run without error
        2 = same, i.e. output same as in textbook
    """
    # no source code
    if len(cell2['source']) == 0:
        return 0

    # untouched empty source code (with default placeholder)
    if cell2['source'] == const.SOURCE_PH:
        return 0

    # if outputs is empty, we have two different possibility
    if len(cell2['outputs']) == 0:
        # code not run: if outputs in textbook is not empty, or
        # cannot determined: if outputs in textbook is also empty, 
        #   - in such case we consider it as *correct*
        if len(cell1['outputs']) > 0:
            return 0
        else:
            return 2

    # the normal case, not empty source and outputs, compare the outputs below
    # nbformat>=4 support 4 output types: stream, display_data, execute_result, error
    # see also: https://ipython.readthedocs.io/en/3.x/notebook/nbformat.html
    for index, output2 in enumerate(cell2['outputs']):
        type2 = output2['output_type']
        lines2 = []
        if type2 == 'error':
            return 0

        if type2 == 'stream':
            lines2 = output2['text']
        else:
            # type display_data and execute_result are similar
            lines2 = output2['data']['text/plain']

        output1 = cell1['outputs'][index]
        lines1 = output1['text'] if output1['output_type'] == 'stream' else output1['data']['text/plain']
        return (2 if lines2 == lines1 else 1)


def check_cells(cells1, cells2):
    """
    Check cells of completed student book (cells1) with original ones (cells2)
    Return a list of int numbers, each element contains result of one cell （same order with original textbook）:
        0 - empty, 1 - not empty, 2 - same as original
    """
    l = []

    for index, cell1 in enumerate(cells1):
        if cell1['cell_type'] == 'code':
            cell2 = cells2[index]
            l.append(check_cell(cell1, cell2))

    return l


def check_book(p1, p2):
    """
    Check completed student book (p2) with original textbook (p1)
    Return a dict include the following key-values:
    total:     total count of code cells
    completed： count of completed code cells (both cell and output are not empty)
    correct:   count of correct code cells (the output is exactly the same as original textbook)
    details:   a list of int numbers, each of which element is the checkup result of a code cell （same order with original textbook）
    error:     a int error code when things going bad
               0 - no error, 1 - unknown error, 2 - file error, 3 - nbformat version error, etc.
    """
    result = {
        'total': 0,
        'completed': 0,
        'correct': 0,
        'details': [],
        'error': 1
    }

    try:
        textbook = nbformat.read(str(p1), as_version=nbformat.NO_CONVERT)
        studentbook = nbformat.read(str(p2), as_version=nbformat.NO_CONVERT)
    except Exception as e:
        result['error'] = 2
        return result

    if textbook['nbformat'] < 4 or studentbook['nbformat'] < 4:
        result['error'] = 3
        return result

    try:
        l = check_cells(textbook['cells'], studentbook['cells'])
        result['total'] = len(l)
        result['completed'] = sum(map(lambda x: x > 0, l))
        result['correct'] = sum(map(lambda x: x == 2, l))
        result['details'] = l
        result['error'] = 0
        return result
    except:
        result['error'] = 1
        return result


if __name__ == '__main__':
    result = check_book(Path('demo.ipynb'), Path('redacted.ipynb'))
    print(result)