import ast
import pathlib


ROOT = pathlib.Path(__file__).resolve().parents[1]
PROJECT_PATH = ROOT / 'Project.py'


def read_source():
    return PROJECT_PATH.read_text()


def test_syntax_compiles():
    src = read_source()
    # Ensure the file compiles (no SyntaxError)
    compile(src, str(PROJECT_PATH), 'exec')


def test_detect_infinite_prompt_loop():
    src = read_source()
    tree = ast.parse(src, filename=str(PROJECT_PATH))

    # Find while loops that compare `prompt` against the literal 'quit'
    issues = []
    for node in ast.walk(tree):
        if isinstance(node, ast.While):
            # Simple binary comparison prompt != 'quit'
            test = node.test
            compares_prompt_to_quit = False
            if isinstance(test, ast.Compare):
                left = test.left
                comparators = test.comparators
                if isinstance(left, ast.Name) and left.id == 'prompt':
                    for comp in comparators:
                        if isinstance(comp, ast.Constant) and isinstance(comp.value, str) and comp.value == 'quit':
                            compares_prompt_to_quit = True

            if compares_prompt_to_quit:
                # Check whether the loop body updates `prompt` or calls input()
                updates_prompt = False
                for inner in ast.walk(node):
                    if isinstance(inner, ast.Assign):
                        for target in inner.targets:
                            if isinstance(target, ast.Name) and target.id == 'prompt':
                                updates_prompt = True
                    if isinstance(inner, ast.Call):
                        # input(...) inside the loop
                        if isinstance(inner.func, ast.Name) and inner.func.id == 'input':
                            updates_prompt = True

                if not updates_prompt:
                    issues.append((node.lineno, 'while prompt != "quit" without updating prompt inside loop'))

    assert not issues, f'Potential infinite loop(s) found: {issues}'
