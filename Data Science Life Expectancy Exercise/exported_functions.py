import pandas as pd
import numpy as np
import cv2
import skimage
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression


def replace_name(table_column, old_name, new_name):
    """
    Replaces an old name in a column of a table with a new one
    """

    if not isinstance(table_column, pd.Series):
        return "Please, provide a table column as first argument"
    table_column = table_column.replace({old_name: new_name})
    return table_column


def add_values_to_a_table(table, values_list):
    """
    Adds values to a table by a given values_list (a list with a dictionary with keys(the columns` names) and values)
    """
    df = pd.DataFrame.from_records(values_list)
    table = pd.concat([table, df], ignore_index=True)
    return table


def lin_regr_sklearn(x, y):
    """
    Performs gradient descent by sklearn lib
    """
    linear_regression = LinearRegression()
    linear_regression.fit(x.values.reshape(-1, 1),  y)
    return linear_regression


def prediction_ski(steps, x, y):
    """
    Gets the results from a sklearn linear regression
    function and returns prediction on the base of
    the steps given (rounded to the 2nd decimal)
    """
    if not isinstance(steps, list):
        return "Please, provide steps argument in the form [[5]]"
    res = all(isinstance(ele, list) for ele in steps)
    if res:
        lin_regr_results = lin_regr_sklearn(x,y)
        prediction = lin_regr_results.predict(steps)[0]
        return round(prediction, 2)
    else:
        return "Please, provide steps argument in the form [[5]]"


def convert_to_grayscale(images):
    """
    Converts the specified RGB image to grayscale, averaging over
    the red, green, and blue channels
    """
    gray_images = []
    for image in images:
        image = (image.sum(axis=2))/3
        image = np.ceil(image)
        image = np.uint8(image)
        gray_images.append(image)
    return gray_images



def rotate_images(images):
    """
    Rotates every image from a list of images with an angle: -90
    """
    rotated_images = []
    for image in images:
        image = skimage.transform.rotate(image, -90, resize = True, preserve_range = True)
        rotated_images.append(image)
    return rotated_images


def show_images(images):
    """
    Shows image from a list of images
    """
    for image in images:
        plt.figure(figsize = (10, 8))
        plt.imshow(image, cmap = "gray")
        plt.show()


def crop_image(image, top, bottom, left, right):
    """
    Crops a grayscale image to the specified box,
    leaving inside the cropped image
    """
    cropped = image[top:bottom,left:right]
    return cropped


def resize_images(images):
    """
    Resizes all images to have the same width
    """
    max_width = max([image.shape[1] for image in images])
    padded_images = [np.pad(image, ((0, 0), (0, max_width - image.shape[1])), mode = "constant", constant_values = 255) for image in images]
    return padded_images


def concatenate_images(images):
    """
    Concatenates all images vertically (one below the other)
    """
    images = resize_images(images)
    im_v = cv2.vconcat(images)
    return im_v


def threshold_image(image, low, high):
    """
    Make the image with higher contrast by
    transofrming close pixels to black into black,
    close pixels to white into white.
    """
    image_bw = image.copy()
    image_bw[image_bw <= low] = 0
    image_bw[high < image_bw] = 255
    return image_bw


def remove_empty_elements(a_list):
    """
    Removes empty elements from a list
    """
    for el in a_list:
        if el == "":
            a_list.remove(el)
    return a_list


def remove_empty_entries_and_lines(a_matrix):
    """
    In a matrix removes empty elements, swaps empty lines (\n) with empty spaces
    """
    for el in a_matrix:
        for elinside in el:
            if elinside == "":
                el.remove(elinside)

            if "\n" in elinside:
                while "\n" in elinside:
                    new_string = elinside[0: elinside.index("\n")] + ' ' + elinside[elinside.index("\n") + 1:]
                    el[el.index(elinside)] = new_string
                    elinside = new_string
    return a_matrix


def create_table(a_mat):
    """
    Generates a table on the base of a matrix
    """
    df_dict = {}
    for column_list in a_mat:
        df_dict[column_list[0]] = column_list[1:]
    tabl = pd.DataFrame(df_dict)
    return tabl


