import argparse
import matplotlib.pyplot as plt

import pandas as pd
import numpy as np


def calculate_mse_for_test(x, y, w, iterations):
    error = 0
    for i in range(0, iterations):
        h = np.dot(x, w)

        mse = np.sum(np.square(h - y))
        mse /= y.size
        error += mse
    return error


def fit(x, y, alfa, iterations):
    w = np.zeros((x.shape[1], 1))
    costs = []
    error = 0

    for i in range(0, iterations):
        h = np.dot(x, w)

        # calculate cost
        cost = np.sum(np.square(h - y))
        cost /= 2 * y.size
        costs.append(cost)

        mse = np.sum(np.square(h - y))
        mse /= y.size
        error += mse

        # calculate new w
        dw = np.dot(x.T, h - y)
        dw /= y.shape[1]
        w -= alfa * dw
    # print(w)

    return w, costs, error


def get_values(values):
    y = values[:, -1]
    y = y.reshape(y.shape[0], 1)
    y = y.astype(np.int)
    x = values[:, :-1]
    x = x.astype(np.int)
    return x, y


def normalize_matrix(x):
    x_max = x.max(axis=0)
    x = x / (x_max + np.spacing(0))
    return x, x_max


def predict_price(rooms, square_footage, w, x_train_max, y_train_max):
    x = np.array([rooms, square_footage], dtype=int)
    x = x / x_train_max  # normalize input parameters
    price = (np.dot(x, w[1:]) + w[0]) * y_train_max  # denormalized price
    print('Predicted prize is: {:.2f}'.format(price[0]))


def evaluate_new_apartment(rooms, square_footage, alfa, iterations):
    # divide dependent and independent training and test values
    train = pd.read_csv('predict_models/train.csv')
    test = pd.read_csv('predict_models/test.csv')

    x_train, y_train = get_values(train.values)
    x_test, y_test = get_values(test.values)

    # normalize data
    x_train, x_train_max = normalize_matrix(x_train)
    y_train, y_train_max = normalize_matrix(y_train)
    x_test, x_test_max = normalize_matrix(x_test)
    y_test, y_test_max = normalize_matrix(y_test)

    # add column of ones due to the free term of the equation
    x_train = np.vstack((np.ones((x_train.shape[0],)), x_train.T)).T
    x_test = np.vstack((np.ones((x_test.shape[0],)), x_test.T)).T

    w, costs, mse = fit(x_train, y_train, alfa, iterations)
    mse_test = calculate_mse_for_test(x_test, y_test, w, iterations)

    rn = np.arange(0, iterations)
    plt.plot(rn, costs)
    plt.show()
    print('MSE for train is: {}'.format(mse))
    print('MSE for test is: {}'.format(mse_test))

    # predict_price()
    predict_price(rooms, square_footage, w, x_train_max, y_train_max)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--rooms', default=2)
    parser.add_argument('--square_footage', default=60)
    parser.add_argument('--alfa', default=0.0001)
    parser.add_argument('--iterations', default=2000)
    rooms = int(parser.parse_args().rooms)
    square_footage = int(parser.parse_args().square_footage)
    alfa = float(parser.parse_args().alfa)
    iterations = int(parser.parse_args().iterations)
    evaluate_new_apartment(rooms, square_footage, alfa, iterations)
