#!/usr/bin/env python
"""Execute the tests for the razers3 program.

The golden test outputs are generated by the script generate_outputs.sh.

You have to give the root paths to the source and the binaries as arguments to
the program.  These are the paths to the directory that contains the 'projects'
directory.

Usage:  run_tests.py SOURCE_ROOT_PATH BINARY_ROOT_PATH
"""
import logging
import os.path
import sys

# Automagically add util/py_lib to PYTHONPATH environment variable.
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..',
                                    '..', '..', 'util', 'py_lib'))
sys.path.insert(0, path)

import seqan.app_tests as app_tests

class RemovePairIdColumn(object):
    """Transformation to remove pair id column."""
    
    def __init__(self, col_no=8, min_cols=8):
        # The index of the column to remove.
        self.col_no = col_no
        # If there are less than min_col columns then we don't remove.
        self.min_cols = min_cols

    def apply(self, text, is_left):
        lines = text.splitlines(True)
        lines2 = []
        for line in lines:
            cols = line.split('\t')
            if len(cols) > self.min_cols:
                cols = cols[0:self.col_no] + cols[self.col_no + 1:]
            lines2.append('\t'.join(cols))
        return ''.join(lines2)


def main(source_base, binary_base):
    """Main entry point of the script."""

    print 'Executing test for razers3'
    print '==========================='
    print

    ph = app_tests.TestPathHelper(
        source_base, binary_base,
        'extras/apps/razers3/tests')  # tests dir

    # ============================================================
    # Auto-detect the binary path.
    # ============================================================

    path_to_program = app_tests.autolocateBinary(
      binary_base, 'extras/apps/razers3', 'razers3')

    # ============================================================
    # Built TestConf list.
    # ============================================================

    # Build list with TestConf objects, analoguely to how the output
    # was generated in generate_outputs.sh.
    conf_list = []

    # We prepare a list of transforms to apply to the output files.  This is
    # used to strip the input/output paths from the programs' output to
    # make it more canonical and host independent.
    ph.outFile('-')  # To ensure that the out path is set.
    transforms = [
        app_tests.ReplaceTransform(os.path.join(ph.source_base_path, 'extras/apps/razers3/tests') + os.sep, '', right=True),
        app_tests.ReplaceTransform(ph.temp_dir + os.sep, '', right=True),
        ]

    # Transforms for SAM output format only.  Make VN field of @PG header canonical.
    sam_transforms = [app_tests.RegexpReplaceTransform(r'\tVN:[^\t]*', r'\tVN:VERSION', right=True, left=True)]

    # Transforms for RazerS output format only.  Remove pair id column.
    razers_transforms = [RemovePairIdColumn()]

    # ============================================================
    # Run Adeno Single-End Tests
    # ============================================================

    # We run the following for all read lengths we have reads for.
    for rl in [36, 100]:
        # Run with default options.
        conf = app_tests.TestConf(
            program=path_to_program,
            redir_stdout=ph.outFile('se-adeno-reads%d_1.stdout' % rl),
            args=[ph.inFile('adeno-genome.fa'),
                  ph.inFile('adeno-reads%d_1.fa' % rl),
                  '-o', ph.outFile('se-adeno-reads%d_1.razers' % rl)],
            to_diff=[(ph.inFile('se-adeno-reads%d_1.razers' % rl),
                      ph.outFile('se-adeno-reads%d_1.razers' % rl)),
                     (ph.inFile('se-adeno-reads%d_1.stdout' % rl),
                      ph.outFile('se-adeno-reads%d_1.stdout' % rl))])
        conf_list.append(conf)

        # Allow indels.
        conf = app_tests.TestConf(
            program=path_to_program,
            redir_stdout=ph.outFile('se-adeno-reads%d_1-ng.stdout' % rl),
            args=['-ng',
                  ph.inFile('adeno-genome.fa'),
                  ph.inFile('adeno-reads%d_1.fa' % rl),
                  '-o', ph.outFile('se-adeno-reads%d_1-ng.razers' % rl)],
            to_diff=[(ph.inFile('se-adeno-reads%d_1-ng.razers' % rl),
                      ph.outFile('se-adeno-reads%d_1-ng.razers' % rl)),
                     (ph.inFile('se-adeno-reads%d_1-ng.stdout' % rl),
                      ph.outFile('se-adeno-reads%d_1-ng.stdout' % rl))])
        conf_list.append(conf)

        # Compute forward/reverse matches only.
        for o in ['-r', '-f']:
            conf = app_tests.TestConf(
                program=path_to_program,
                redir_stdout=ph.outFile('se-adeno-reads%d_1%s.stdout' % (rl, o)),
                args=[o,
                      ph.inFile('adeno-genome.fa'),
                      ph.inFile('adeno-reads%d_1.fa' % rl),
                      '-o', ph.outFile('se-adeno-reads%d_1%s.razers' % (rl, o))],
                to_diff=[(ph.inFile('se-adeno-reads%d_1%s.razers' % (rl, o)),
                          ph.outFile('se-adeno-reads%d_1%s.razers' % (rl, o))),
                         (ph.inFile('se-adeno-reads%d_1%s.stdout' % (rl, o)),
                          ph.outFile('se-adeno-reads%d_1%s.stdout' % (rl, o)))])
            conf_list.append(conf)

        # Compute with different identity rates.
        for i in range(90, 101):
            conf = app_tests.TestConf(
                program=path_to_program,
                redir_stdout=ph.outFile('se-adeno-reads%d_1-i%d.stdout' % (rl, i)),
                args=['-i', str(i),
                      ph.inFile('adeno-genome.fa'),
                      ph.inFile('adeno-reads%d_1.fa' % rl),
                      '-o', ph.outFile('se-adeno-reads%d_1-i%d.razers' % (rl, i))],
                to_diff=[(ph.inFile('se-adeno-reads%d_1-i%d.razers' % (rl, i)),
                          ph.outFile('se-adeno-reads%d_1-i%d.razers' % (rl, i))),
                         (ph.inFile('se-adeno-reads%d_1-i%d.stdout' % (rl, i)),
                          ph.outFile('se-adeno-reads%d_1-i%d.stdout' % (rl, i)))])
            conf_list.append(conf)

        # Compute with different output formats.
        for of, suffix in enumerate(['razers', 'fa', 'eland', 'gff', 'sam', 'afg']):
            this_transforms = list(transforms)
            if suffix == 'razers':
                this_transforms += razers_transforms
            elif suffix == 'sam':
                this_transforms += sam_transforms
            conf = app_tests.TestConf(
                program=path_to_program,
                redir_stdout=ph.outFile('se-adeno-reads%d_1-of%d.stdout' % (rl, of)),
                args=[    ph.inFile('adeno-genome.fa'),
                      ph.inFile('adeno-reads%d_1.fa' % rl),
                      '-o', ph.outFile('se-adeno-reads%d_1-of%d.%s' % (rl, of, suffix))],
                to_diff=[(ph.inFile('se-adeno-reads%d_1-of%d.%s' % (rl, of, suffix)),
                          ph.outFile('se-adeno-reads%d_1-of%d.%s' % (rl, of, suffix)),
                          this_transforms),
                         (ph.inFile('se-adeno-reads%d_1-of%d.stdout' % (rl, of)),
                          ph.outFile('se-adeno-reads%d_1-of%d.stdout' % (rl, of)),
                          transforms)])
            conf_list.append(conf)

        # Compute with different sort orders.
        for so in [0, 1]:
            conf = app_tests.TestConf(
                program=path_to_program,
                redir_stdout=ph.outFile('se-adeno-reads%d_1-so%d.stdout' % (rl, so)),
                args=['-so', str(so),
                      ph.inFile('adeno-genome.fa'),
                      ph.inFile('adeno-reads%d_1.fa' % rl),
                      '-o', ph.outFile('se-adeno-reads%d_1-so%d.razers' % (rl, so))],
                to_diff=[(ph.inFile('se-adeno-reads%d_1-so%d.razers' % (rl, so)),
                          ph.outFile('se-adeno-reads%d_1-so%d.razers' % (rl, so))),
                         (ph.inFile('se-adeno-reads%d_1-so%d.stdout' % (rl, so)),
                          ph.outFile('se-adeno-reads%d_1-so%d.stdout' % (rl, so)))])
            conf_list.append(conf)

    # ============================================================
    # Run Adeno Paired-End Tests
    # ============================================================

    # We run the following for all read lengths we have reads for.
    for rl in [36, 100]:
        # Run with default options.
        conf = app_tests.TestConf(
            program=path_to_program,
            redir_stdout=ph.outFile('pe-adeno-reads%d_2.stdout' % rl),
            args=[ph.inFile('adeno-genome.fa'),
                  ph.inFile('adeno-reads%d_1.fa' % rl),
                  ph.inFile('adeno-reads%d_2.fa' % rl),
                  '-o', ph.outFile('pe-adeno-reads%d_2.razers' % rl)],
            to_diff=[(ph.inFile('pe-adeno-reads%d_2.razers' % rl),
                      ph.outFile('pe-adeno-reads%d_2.razers' % rl),
                      razers_transforms),
                     (ph.inFile('pe-adeno-reads%d_2.stdout' % rl),
                      ph.outFile('pe-adeno-reads%d_2.stdout' % rl))])
        conf_list.append(conf)

        # Allow indels.
        conf = app_tests.TestConf(
            program=path_to_program,
            redir_stdout=ph.outFile('pe-adeno-reads%d_2.stdout' % rl),
            args=[ph.inFile('adeno-genome.fa'),
                  ph.inFile('adeno-reads%d_1.fa' % rl),
                  ph.inFile('adeno-reads%d_2.fa' % rl),
                  '-o', ph.outFile('pe-adeno-reads%d_2.razers' % rl)],
            to_diff=[(ph.inFile('pe-adeno-reads%d_2.razers' % rl),
                      ph.outFile('pe-adeno-reads%d_2.razers' % rl),
                      razers_transforms),
                     (ph.inFile('pe-adeno-reads%d_2.stdout' % rl),
                      ph.outFile('pe-adeno-reads%d_2.stdout' % rl))])
        conf_list.append(conf)

        # Compute forward/reverse matches only.
        for o in ['-r', '-f']:
            conf = app_tests.TestConf(
                program=path_to_program,
                redir_stdout=ph.outFile('pe-adeno-reads%d_2%s.stdout' % (rl, o)),
                args=[o,
                      ph.inFile('adeno-genome.fa'),
                      ph.inFile('adeno-reads%d_1.fa' % rl),
                      ph.inFile('adeno-reads%d_2.fa' % rl),
                      '-o', ph.outFile('pe-adeno-reads%d_2%s.razers' % (rl, o))],
                to_diff=[(ph.inFile('pe-adeno-reads%d_2%s.razers' % (rl, o)),
                          ph.outFile('pe-adeno-reads%d_2%s.razers' % (rl, o)),
                          razers_transforms),
                         (ph.inFile('pe-adeno-reads%d_2%s.stdout' % (rl, o)),
                          ph.outFile('pe-adeno-reads%d_2%s.stdout' % (rl, o)))])
            conf_list.append(conf)

        # Compute with different identity rates.
        for i in range(90, 101):
            conf = app_tests.TestConf(
                program=path_to_program,
                redir_stdout=ph.outFile('pe-adeno-reads%d_2-i%d.stdout' % (rl, i)),
                args=['-i', str(i),
                      ph.inFile('adeno-genome.fa'),
                      ph.inFile('adeno-reads%d_1.fa' % rl),
                      ph.inFile('adeno-reads%d_2.fa' % rl),
                      '-o', ph.outFile('pe-adeno-reads%d_2-i%d.razers' % (rl, i))],
                to_diff=[(ph.inFile('pe-adeno-reads%d_2-i%d.razers' % (rl, i)),
                          ph.outFile('pe-adeno-reads%d_2-i%d.razers' % (rl, i)),
                          razers_transforms),
                         (ph.inFile('pe-adeno-reads%d_2-i%d.stdout' % (rl, i)),
                          ph.outFile('pe-adeno-reads%d_2-i%d.stdout' % (rl, i)))])
            conf_list.append(conf)

        # Compute with different output formats.
        for of, suffix in enumerate(['razers', 'fa', 'eland', 'gff', 'sam', 'afg']):
            this_transforms = list(transforms)
            if suffix == 'razers':
                this_transforms += razers_transforms
            elif suffix == 'sam':
                this_transforms += sam_transforms
            conf = app_tests.TestConf(
                program=path_to_program,
                redir_stdout=ph.outFile('pe-adeno-reads%d_2-of%d.stdout' % (rl, of)),
                args=[    ph.inFile('adeno-genome.fa'),
                      ph.inFile('adeno-reads%d_1.fa' % rl),
                      ph.inFile('adeno-reads%d_2.fa' % rl),
                      '-o', ph.outFile('pe-adeno-reads%d_2-of%d.%s' % (rl, of, suffix))],
                to_diff=[(ph.inFile('pe-adeno-reads%d_2-of%d.%s' % (rl, of, suffix)),
                          ph.outFile('pe-adeno-reads%d_2-of%d.%s' % (rl, of, suffix)),
                          this_transforms),
                         (ph.inFile('pe-adeno-reads%d_2-of%d.stdout' % (rl, of)),
                          ph.outFile('pe-adeno-reads%d_2-of%d.stdout' % (rl, of)),
                          this_transforms)])
            conf_list.append(conf)

        # Compute with different sort orders.
        for so in [0, 1]:
            conf = app_tests.TestConf(
                program=path_to_program,
                redir_stdout=ph.outFile('pe-adeno-reads%d_2-so%d.stdout' % (rl, so)),
                args=['-so', str(so),
                      ph.inFile('adeno-genome.fa'),
                      ph.inFile('adeno-reads%d_1.fa' % rl),
                      ph.inFile('adeno-reads%d_2.fa' % rl),
                      '-o', ph.outFile('pe-adeno-reads%d_2-so%d.razers' % (rl, so))],
                to_diff=[(ph.inFile('pe-adeno-reads%d_2-so%d.razers' % (rl, so)),
                          ph.outFile('pe-adeno-reads%d_2-so%d.razers' % (rl, so)),
                          razers_transforms),
                         (ph.inFile('pe-adeno-reads%d_2-so%d.stdout' % (rl, so)),
                          ph.outFile('pe-adeno-reads%d_2-so%d.stdout' % (rl, so)))])
            conf_list.append(conf)

    # Execute the tests.
    failures = 0
    for conf in conf_list:
        res = app_tests.runTest(conf)
        # Output to the user.
        print ' '.join(['razers3'] + conf.args),
        if res:
             print 'OK'
        else:
            failures += 1
            print 'FAILED'

    # Cleanup.
    ph.deleteTempDir()

    print '=============================='
    print '     total tests: %d' % len(conf_list)
    print '    failed tests: %d' % failures
    print 'successful tests: %d' % (len(conf_list) - failures)
    print '=============================='
    # Compute and return return code.
    return failures != 0


if __name__ == '__main__':
    sys.exit(app_tests.main(main))
