import argparse
from robot.api import get_model
from .code_formatters import SplitToMultiline, KeywordRenamer, AlignSelected, WhitespaceCleanup, TabsToSpaces


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-m',
        '--modes'
    )
    parser.add_argument('-p', '--path', required=True)
    parser.add_argument('-l', '--line', type=int)
    parser.add_argument('-el', '--end-line', type=int)
    parser.add_argument('-i', '--ignore', help='List of keyword names to ignore')
    parser.add_argument('--indent', default=4, type=int)
    parser.add_argument('--separator', default=4, type=int)
    args = parser.parse_args()

    if not args.modes:
        return
    modes = args.modes.split(',')
    formatters = []
    if 'split' in modes or 'all' in modes:
        formatters.append(SplitToMultiline(args.line, args.end_line, args.separator))
    if 'rename' in modes or 'all' in modes:
        formatters.append(KeywordRenamer(args.ignore))
    if 'align' in modes or 'all' in modes:
        formatters.append(AlignSelected(args.line, args.end_line, args.indent))
    if 'tabs_to_spaces' in modes or 'all' in modes:
        formatters.append(TabsToSpaces())
    if 'whitespace' in modes or 'all' in modes:
        formatters.append(WhitespaceCleanup())

    model = get_model(args.path)
    for formatter in formatters:
        formatter.visit(model)
    model.save()
