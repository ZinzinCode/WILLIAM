import time
from william_diagnostics import tester, fixer, explainer, feedback

def run_monitor():
    while True:
        for module_name, test_func in tester.modules.items():
            try:
                test_func()
            except Exception as e:
                readable = explainer.explain_error(e)
                fixer.try_fix(module_name, e)
                feedback.notify_user(module_name, readable, e)
        time.sleep(10)
