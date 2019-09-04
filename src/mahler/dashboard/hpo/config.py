dataset_names = ['mnist', 'svhn', 'cifar10', 'cifar100', 'emnist', 'tinyimagenet']
# dataset_names = ['svhn', 'emnist', 'tinyimagenet']
# dataset_names = ['tinyimagenet']
distrib_names = ['min']  #  'max', 'mean']
model_names = [
    'lenet', 'mobilenetv2',
    'vgg11', 'vgg19',
    'resnet18', 'resnet101',
    'densenet121', 'densenet201',
    'preactresnet18', 'preactresnet101']
# model_names = ['lenet', 'vgg11', 'resnet18']
algo_names = ['asha']

versions = ['beta-v8.0.0', 'beta-v8.1.0', 'beta-v8.1.1', 'beta-v8.2.0', 'beta-v8.3.0']
# versions = ['v4.2.3', 'v4.2.4', 'v4.2.5', 'v4.2.6', 'v5.0.0', 'beta-v8.0.0', 'beta-v8.1.1',
#                 'beta-v8.2.0', 'beta-v8.3.0']

max_ressource = 30

# TODO: Add colors


# TODO: Add config for axis

# yaxis = dict(
#     mnist=dict(
#         'summary': [0.003, 0.01],
#         'evolution': [0.001, 0.02],
#         'curves': [0.001, 0.9],
#         'distrib': [0.003, 0.13],
#         ))
