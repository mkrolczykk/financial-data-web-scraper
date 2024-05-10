"""
Regex engine library

Supported regex patterns:
    * Literals (`abc`)
    * Sets (`[abc]`)
    * Star/question mark/plus (`a*b?c+`)
    * Alternates (`a|b`)
    * Start and end (`^abc$`)
    * Matching in the middle of a string a returning the match
    * Custom escape sequences (`\a \d`)

"""


def _is_start(char):
    return char == '^'


def _is_end(char):
    return char == '$'


def _is_star(char):
    return char == '*'


def _is_plus(char):
    return char == '+'


def _is_question(char):
    return char == '?'


def _is_operator(char):
    return _is_star(char) or _is_plus(char) or _is_question(char)


def _is_dot(char):
    return char == '.'


def _is_escape_sequence(term):
    return _is_escape(term[0])


def _is_escape(char):
    return char == '\\'


def _is_open_alternate(char):
    return char == '('


def _is_close_alternate(char):
    return char == ')'


def _is_open_set(char):
    return char == '['


def _is_close_set(char):
    return char == ']'


def _is_literal(char):
    return char.isalpha() or char.isdigit() or char in ' :/'


def _is_alternate(term):
    return _is_open_alternate(term[0]) and _is_close_alternate(term[-1])


def _is_set(term):
    return _is_open_set(term[0]) and _is_close_set(term[-1])


def _is_unit(term):
    return _is_literal(term[0]) or _is_dot(term[0]) or _is_set(term) or _is_escape_sequence(term)


def _split_alternate(alternate):
    return alternate[1:-1].split('|')


def _split_set(set_head):
    set_inside = set_head[1:-1]
    set_terms = list(set_inside)
    return set_terms


def _split_expr(expr):
    head = None
    operator = None
    rest = None
    last_expr_pos = 0

    if _is_open_set(expr[0]):
        last_expr_pos = expr.find(']') + 1
        head = expr[:last_expr_pos]
    elif _is_open_alternate(expr[0]):
        last_expr_pos = expr.find(')') + 1
        head = expr[:last_expr_pos]
    elif _is_escape(expr[0]):
        last_expr_pos += 2
        head = expr[:2]
    else:
        last_expr_pos = 1
        head = expr[0]

    if last_expr_pos < len(expr) and _is_operator(expr[last_expr_pos]):
        operator = expr[last_expr_pos]
        last_expr_pos += 1

    rest = expr[last_expr_pos:]

    return head, operator, rest


def _does_unit_match(expr, string):
    head, operator, rest = _split_expr(expr)

    if len(string) == 0:
        return False
    if _is_literal(head):
        return expr[0] == string[0]
    elif _is_dot(head):
        return True
    elif _is_escape_sequence(head):
        if head == '\\a':
            return string[0].isalpha()
        elif head == '\\d':
            return string[0].isdigit()
        else:
            return False
    elif _is_set(head):
        set_inside = head[1:-1]
        return string[0] in set_inside or (ord(set_inside[0]) <= ord(string[0]) <= ord(set_inside[-1]))
    return False



def _match_multiple(expr, string, match_length, min_match_length=None, max_match_length=None):
    head, operator, rest = _split_expr(expr)

    if not min_match_length:
        min_match_length = 0

    submatch_length = -1

    while not max_match_length or (submatch_length < max_match_length):
        [subexpr_matched, subexpr_length] = _match_expr(
            (head * (submatch_length + 1)), string, match_length
        )
        if subexpr_matched:
            submatch_length += 1
        else:
            break

    while submatch_length >= min_match_length:
        [matched, new_match_length] = _match_expr(
            (head * submatch_length) + rest, string, match_length
        )
        if matched:
            return [matched, new_match_length]
        submatch_length -= 1

    return [False, None]


def _match_star(expr, string, match_length):
    return _match_multiple(expr, string, match_length, None, None)


def _match_plus(expr, string, match_length):
    return _match_multiple(expr, string, match_length, 1, None)


def _match_question(expr, string, match_length):
    return _match_multiple(expr, string, match_length, 0, 1)


def _match_alternate(expr, string, match_length):
    head, operator, rest = _split_expr(expr)
    options = _split_alternate(head)

    for option in options:
        [matched, new_match_length] = _match_expr(
            option + rest, string, match_length
        )
        if matched:
            return [matched, new_match_length]

    return [False, None]


def _match_expr(expr, string, match_length=0):
    if len(expr) == 0:
        return [True, match_length]
    elif _is_end(expr[0]):
        if len(string) == 0:
            return [True, match_length]
        else:
            return [False, None]

    head, operator, rest = _split_expr(expr)

    if _is_star(operator):
        return _match_star(expr, string, match_length)
    elif _is_plus(operator):
        return _match_plus(expr, string, match_length)
    elif _is_question(operator):
        return _match_question(expr, string, match_length)
    elif _is_alternate(head):
        return _match_alternate(expr, string, match_length)
    elif _is_unit(head):
        if _does_unit_match(head, string):
            return _match_expr(rest, string[1:], match_length + 1)
    else:
        print(f'Unknown token in expr {expr}.')

    return [False, None]


def match(expr, string):
    match_pos = 0
    matched = False
    if _is_start(expr[0]):
        max_match_pos = 0
        expr = expr[1:]
    else:
        max_match_pos = len(string)
    while not matched and match_pos <= max_match_pos:
        [matched, match_length] = _match_expr(expr, string[match_pos:])
        if matched:
            return [matched, match_pos, match_length]
        match_pos += 1
    return [False, None, None]

