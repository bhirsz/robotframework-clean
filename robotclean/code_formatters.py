import ast
from collections import defaultdict
from robot.api import Token
from robot.utils.misc import printable_name
from robot.parsing.model import Statement, ForLoop
from robot.parsing.model.statements import EmptyLine, Comment
from robot.parsing.model.visitor import ModelVisitor


class SplitToMultiline(ast.NodeVisitor):
    def __init__(self, line, end_line, separator):
        self.tree = {
            'runkeywordif',
            'setvariableif',
            'settodictionary',
            'removefromdictionary'
        }
        self.ignore_chars = {
            'SEPARATOR',
            'EOL',
            'CONTINUATION'
        }
        self.line = line
        self.end_line = end_line or line
        self.separator = separator

    def insert_seperator(self, iterator):
        for elem in iterator:
            yield elem
            yield Token(Token.SEPARATOR, self.separator * ' ')

    def split_to_new_line(self, iterator, indent, not_split_first=False):
        iter_gen = (elem for elem in iterator)
        if not_split_first:
            elem = next(iter_gen)
            yield Token(Token.SEPARATOR, self.separator * ' ')
            yield elem
        for elem in iter_gen:
            yield Token(Token.EOL, '\n')
            yield indent
            yield Token(Token.CONTINUATION, '...')
            yield Token(Token.SEPARATOR, self.separator * ' ')
            yield elem
        yield Token(Token.EOL, '\n')

    def visit_KeywordCall(self, node):  # noqa
        if node.lineno < self.line or node.lineno > self.end_line:
            return
        indent = node.tokens[0]
        args = defaultdict(list)
        keyword_token = None
        for child in node.tokens:
            if child.type in self.ignore_chars:
                continue
            if child.type == 'KEYWORD':
                keyword_token = child
                continue
            args[child.type].append(child)
        assign = list(self.insert_seperator(args['ASSIGN']))
        not_split_first = self.is_nested_tree(keyword_token)
        arguments = list(self.split_to_new_line(args['ARGUMENT'], indent, not_split_first))
        tokens = [indent] + assign
        tokens.append(keyword_token)
        tokens.extend(arguments)
        node.tokens = tokens

    @staticmethod
    def normalize_name(name):
        return name.replace('_', '').replace(' ', '').lower()

    def is_nested_tree(self, token):
        if not token.value:
            return False
        return self.normalize_name(token.value) in self.tree


class KeywordRenamer(ast.NodeVisitor):
    def __init__(self, ignore):
        self.ignore = ignore

    def rename_token(self, token):
        if token is None or (self.ignore and self.ignore in token.value):
            return
        token.value = printable_name(token.value, code_style=True)

    def visit_KeywordName(self, node):  # noqa
        token = node.get_token(Token.KEYWORD_NAME)
        self.rename_token(token)

    def visit_KeywordCall(self, node):  # noqa
        token = node.get_token(Token.KEYWORD)
        self.rename_token(token)

    def visit_File(self, node):  # noqa
        self.generic_visit(node)

    def visit_Keyword(self, node):  # noqa
        self.generic_visit(node)

    def visit_TestCase(self, node):  # noqa
        self.generic_visit(node)

    def visit_SuiteSetup(self, node):  # noqa
        self.generic_visit(node)

    def visit_TestSetup(self, node):  # noqa
        self.generic_visit(node)

    def visit_Setup(self, node):  # noqa
        self.generic_visit(node)

    def visit_SuiteTeardown(self, node):  # noqa
        self.generic_visit(node)

    def visit_TestTeardown(self, node):  # noqa
        self.generic_visit(node)

    def visit_Teardown(self, node):  # noqa
        self.generic_visit(node)


class AlignSelected(ast.NodeVisitor):
    def __init__(self, start_line, end_line, indent):
        self.start_line = start_line
        self.end_line = end_line
        self.indent = indent

    def visit_TestCase(self, node):  # noqa
        self.align(node, self.indent)

    def visit_Keyword(self, node):  # noqa
        self.align(node, self.indent)

    @staticmethod
    def get_longest(matrix, index):
        longest = max(len(r[index].value) for r in matrix if len(r) > index)
        div = longest % 4
        if div:
            longest += 4 - div
        return longest

    def align(self, node, indent):
        if node.end_lineno < self.start_line or node.lineno > self.end_line:
            return
        statements = []
        for child in node.body:
            if isinstance(child, ForLoop):
                self.align(child, indent * 2)
                statements.append(child)
            elif child.type == 'DOCUMENTATION' or self.start_line > child.lineno or self.end_line < child.lineno:
                statements.append(child)
            else:
                statements.append([token for token in child.tokens
                                   if token.type not in ('SEPARATOR', 'CONTINUATION', 'EOL', 'EOS')])
        misaligned_stat = [st for st in statements if isinstance(st, list)]
        if not misaligned_stat:
            return
        col_len = max(len(c) for c in misaligned_stat)
        look_up = [self.get_longest(misaligned_stat, i) for i in range(col_len)]
        node.body = list(self.align_rows(statements, indent, look_up))

    def align_rows(self, statements, indent, look_up):
        for row in statements:
            if isinstance(row, list):
                yield self.align_row(row, indent, look_up)
            else:
                yield row

    @staticmethod
    def align_row(row, indent, look_up):
        aligned_row = [Token(Token.SEPARATOR, indent * ' ')]
        row_len = len(row)
        for i, c in enumerate(row):
            aligned_row.append(c)
            if i < row_len - 1:
                separator = Token(Token.SEPARATOR, (look_up[i] - len(c.value) + 4) * ' ')
                aligned_row.append(separator)
        aligned_row.append(Token(Token.EOL, '\n'))
        return Statement.from_tokens(aligned_row)


class TabsToSpaces(ModelVisitor):
    def visit_Statement(self, node):  # noqa
        for token in node.get_tokens('SEPARATOR'):
            token.value = token.value.expandtabs(4)
        eol_token = node.get_token('EOL')
        if eol_token is not None:
            eol_token.value = '\n'


class WhitespaceCleanup(ast.NodeVisitor):
    def __init__(self):
        self.header_end_lines = 2
        self.test_case_sep = 2
        self.empty_line = Statement.from_tokens([
            Token(Token.EOL, '\n')
        ])

    @staticmethod
    def trim_trailing_empty_lines(node):
        while node.body and isinstance(node.body[-1], EmptyLine):
            node.body.pop()

    @staticmethod
    def trim_leading_empty_lines(node):
        while node.body and isinstance(node.body[0], EmptyLine):
            node.body.pop(0)

    def visit_File(self, node):  # noqa
        self.generic_visit(node)
        if node.sections and node.sections[-1].body:
            self.trim_trailing_empty_lines(node.sections[-1])
        node.sections = [section for section in node.sections if not self.only_empty_lines(section)]

    @staticmethod
    def only_empty_lines(node):
        return all(isinstance(child, EmptyLine) for child in node.body)

    def parse_settings_or_variables(self, node):
        self.trim_trailing_empty_lines(node)
        self.trim_leading_empty_lines(node)
        statements = []
        is_prev_empty_line = False
        for child in node.body:
            if isinstance(child, EmptyLine) and is_prev_empty_line:
                continue
            is_prev_empty_line = isinstance(child, EmptyLine)
            statements.append(child)

        statements.extend([self.empty_line] * self.header_end_lines)
        node.body = statements

    def visit_SettingSection(self, node):  # noqa
        self.parse_settings_or_variables(node)

    def visit_VariableSection(self, node):  # noqa
        self.parse_settings_or_variables(node)

    def visit_CommentSection(self, node):  # noqa
        self.parse_settings_or_variables(node)

    def parse_tests_or_keywords(self, node):
        while node.body and isinstance(node.body[0], EmptyLine):
            node.body.pop(0)
        child = None
        for child in node.body:
            if isinstance(child, Comment):
                continue
            self.trim_leading_empty_lines(child)
            self.trim_trailing_empty_lines(child)
            child.body.append(self.empty_line)
        if child is not None:
            child.body.append(self.empty_line)

    def visit_TestCaseSection(self, node):  # noqa
        self.parse_tests_or_keywords(node)

    def visit_KeywordSection(self, node):  # noqa
        self.parse_tests_or_keywords(node)
