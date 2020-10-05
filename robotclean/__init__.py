import argparse
from robot.api import get_model
from .code_formatters import SplitToMultiline, KeywordRenamer, AlignSelected, WhitespaceCleanup, TabsToSpaces


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-m',
        '--modes',
        required=True
    )
    parser.add_argument('-p', '--path', required=True)
    parser.add_argument('-l', '--line', default=0, type=int)
    parser.add_argument('-el', '--end-line', default=0, type=int)
    parser.add_argument('-i', '--ignore', help='List of keyword names to ignore')
    parser.add_argument('--indent', default=4, type=int)
    parser.add_argument('--separator', default=4, type=int)
    args = parser.parse_args()

    formatters = {
        'split': SplitToMultiline(args.line, args.end_line, args.separator),
        'rename': KeywordRenamer(args.ignore),
        'align': AlignSelected(args.line, args.end_line, args.indent),
        'tabs_to_spaces': TabsToSpaces(),
        'whitespace': WhitespaceCleanup()
    }
    modes = args.modes.split(',')
    model = get_model(args.path)
    for mode in modes:
        if mode not in formatters:
            print(f'Unrecognized mode: "{mode}". Skipping')
            continue
        formatters[mode].visit(model)

    model.save()
