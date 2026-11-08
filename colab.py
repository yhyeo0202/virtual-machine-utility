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

    with tarfile.open('virtualMachineSetup.tar.gz', 'w:gz') as f:
        f.add('virtualMachineSetup')

    listCommand = [
        venvCommand,
        'colab upload -s workspace virtualMachineSetup.tar.gz /content/virtualMachineSetup.tar.gz',
        getExecColabCommand('!tar -xzf /content/virtualMachineSetup.tar.gz'),
        getExecColabCommand('rm /content/virtualMachineSetup.tar.gz'),
        getExecColabCommand('!chmod +x /content/virtualMachineSetup/setup.sh'),
        getExecColabCommand('!/content/virtualMachineSetup/setup.sh')
    ]
    completedProcess = runSubprocess(listCommand)
    os.remove('virtualMachineSetup.tar.gz')

    if completedProcess.returncode != 0:

        return

    listCommand = [
        venvCommand,
        'colab drivemount -s workspace',
        getExecColabCommand(f"!git clone {dictConfig['repository'].format(os.environ['GITHUB_TOKEN'])}")
    ]
    subprocess.Popen(['alacritty', '-e', 'bash', '-c', ' && '.join(listCommand)])

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

    os.makedirs('tmp', exist_ok = True)
    localPath = os.path.join('tmp', sys.argv[1].split('/')[-1])

    if completeProcess.stdout[0] == 'd':
        path = f"{sys.argv[1].split('/')[-1]}.tar.gz"
        localPath = f'{localPath}.tar.gz'
        listCommand = [
            venvCommand,
            getExecColabCommand(f'!tar -czf {path} -C {'/'.join(sys.argv[1].split('/')[:-1])} {path.removesuffix('.tar.gz')}'),
        ]
        completeProcess = runSubprocess(listCommand)

        if completeProcess.returncode != 0:
            
            return
    elif 'No such file or directory' in completeProcess.stdout:

        return

    listCommand = [
        venvCommand,
        f'colab download -s workspace /content/{path} {localPath}',
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

        with tarfile.open(localPath, 'r:gz') as f:
            f.extractall(path = 'tmp')

        os.remove(localPath)

    return

# Have to use !
def exec():
    if len(sys.argv) < 2:
        print('Please specify command to be executed')

        return

    listCommand = [
        venvCommand,
        getExecColabCommand(sys.argv[1])
    ]
    
    subprocess.Popen(['alacritty', '-e', 'bash', '-c', ' && '.join(listCommand)])

    return

def stopSession():
    listCommand = [
        venvCommand,
        'colab stop -s workspace'
    ]
    runSubprocess(listCommand)

    return
