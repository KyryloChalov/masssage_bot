import os

commands = [
    "pip freeze > requirements.txt",
    "pip uninstall -r requirements.txt -y",
]


def run_command(command):
    print("Running command: {}".format(command))
    os.system(command)


for command in commands:
    run_command(command)