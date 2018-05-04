
import argparse
import json
import numpy as np
import sys

import recova.util
from recova.util import eprint, bat_distance
from recova.learning import model_factory


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('algorithm', type=str)
    parser.add_argument('-lr', '--learning_rate', type=float, default=1e-5)
    parser.add_argument('-a', '--alpha', type=float, default=1e-4)
    args = parser.parse_args()

    eprint('Loading document')
    input_document = json.load(sys.stdin)
    eprint('Done loading document')

    sys.stdin = open('/dev/tty')

    predictors = np.array(input_document['data']['predictors'])

    np_examples = []
    covariances = np.empty((len(predictors), 6, 6))
    for i, example_batch in enumerate(input_document['data']['errors']):
        errors = np.array(example_batch)
        covariances[i,:,:] = np.dot(errors.T, errors)

    model = model_factory(args.algorithm)

    model.learning_rate = args.learning_rate
    model.alpha = args.alpha

    learning_run = model.fit(predictors, covariances)
    json.dump(learning_run, sys.stdout)


if __name__ == '__main__':
    cli()
