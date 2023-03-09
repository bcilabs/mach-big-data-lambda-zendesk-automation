from invoke import task
from coverage import Coverage
import json
import os


def set_env():
    env_var = open("env/test.json")
    env_var = json.load(env_var)
    for key in env_var.keys():
        os.environ[key] = env_var[key]
    return "Set variables"


@task(optional="name")
def test(context, name=None):
    set_env()
    run_tests = "pytest -vv test/test_lambda_handler.py --deselect test/test_lambda_handler.py::test_endpoint_response"
    context.run(f"{run_tests}")


@task
def coverage(context):
    min_coverage = 70
    collect_tests = "coverage run -m unittest discover -s test/ -t ."
    set_env()
    context.run(f"{collect_tests}")
    context.run("coverage report")
    cov = Coverage()
    cov.load()
    assert min_coverage <= cov.report()
