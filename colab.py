import os
import subprocess
import sys
import tarfile
import yaml

with open('config.yml', 'r') as f:
    dictConfig = yaml.load(f, Loader = yaml.FullLoader)

venvCommand = 'source venv-virtual-machine-utility/bin/activate'

def runSubprocess(listCommand):
    completedProcess = subprocess.run(
        ' && '.join(listCommand),
        shell = True,
        capture_output = True,
        text = True
    )

    print(completedProcess.stdout)

    if completedProcess.returncode:
        print(completedProcess.stderr)

    return completedProcess

def getExecColabCommand(command):
    execColabCommand = f"echo '{command}' | colab exec -s workspace"

    return execColabCommand

def startSession():
    listCommand = [
        venvCommand,
        'colab sessions'
    ]
    completedProcess = runSubprocess(listCommand)

    if 'workspace' in completedProcess.stdout:
        print('Session exists, do not start a new one')
    else:
        listCommand = [
            venvCommand,
            f"colab new -s workspace{' --gpu T4' if dictConfig['bGpu'] else ''}"
        ]
        runSubprocess(listCommand)

    listCommand = [
        venvCommand,
        'colab upload -s workspace setupVirtualMachine.sh /content/setupVirtualMachine.sh',
        getExecColabCommand('!chmod +x setupVirtualMachine.sh'),
        getExecColabCommand('!./setupVirtualMachine.sh')
    ]
    runSubprocess(listCommand)

    return

def download():
    if len(sys.argv) == 1:
        print('Please specify remote path of file or directory to be downloaded')

        return

    path = sys.argv[1]
    listCommand = [
        venvCommand,
        getExecColabCommand(f'ls -ld {path}'),
    ]
    completeProcess = runSubprocess(listCommand)

    if completeProcess.stdout[0] == 'd':
        path = f'{sys.argv[1]}.tar.gz'
        listCommand = [
            venvCommand,
            getExecColabCommand(f'!tar -czf {path} {sys.argv[1]}'),
        ]
        completeProcess = runSubprocess(listCommand)

        if completeProcess.returncode != 0:
            
            return
    elif 'No such file or directory' in completeProcess.stdout:

        return

    listCommand = [
        venvCommand,
        f'colab download -s workspace /content/{path} {path.split('/')[-1]}',
    ]
    completeProcess = runSubprocess(listCommand)

    if completeProcess.returncode != 0:

        return

    if path.endswith('.tar.gz'):
        listCommand = [
            venvCommand,
            getExecColabCommand(f'rm {path}')
        ]
        runSubprocess(listCommand)

        with tarfile.open(path, 'r:gz') as f:
            f.extractall()

        os.remove(path)

    return

def stopSession():
    listCommand = [
        venvCommand,
        'colab stop -s workspace'
    ]
    runSubprocess(listCommand)

    return
