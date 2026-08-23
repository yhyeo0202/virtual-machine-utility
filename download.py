import colab
import yaml

with open('config.yml', 'r') as f:
    dictConfig = yaml.load(f, Loader = yaml.FullLoader)

match dictConfig['platform']:
    case 'colab':
        colab.download()
