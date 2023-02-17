import matplotlib.pyplot as plt
import pytest
import skimage
import pandas as pd
from exported_functions import *


example_table = pd.DataFrame({
'col1': ["entry1", "entry2", "entry3"],
'col2': [5, 10, 18]
})

test_table = pd.DataFrame({
        'col1': [1, 2, 3, 4],
        'col2': [2, 4, 6, 8]
    })

test_image = np.array([[[1., 1., 1.],
                     [1., 1., 1.],
                     [1., 1., 1.],
                     [1., 1., 1.]],
                    [[1., 0., 0.],
                    [1., 0., 0.],
                    [1., 0., 0.],
                    [1., 0., 0.]]])


def test_replace_name():
    new_column = pd.Series(["new_entry","entry2", "entry3"])
    assert replace_name(example_table['col1'], "entry1", "new_entry").equals(new_column)

def test_replace_name_with_wrong_table_column():
    new_column = ["new_entry","entry2", "entry3"]
    assert replace_name(new_column, "entry1", "new_entry") == "Please, provide a table column as first argument"

def test_replace_name_with_wrong_table_column_table_instead():
    assert replace_name(example_table, "entry1", "new_entry") == "Please, provide a table column as first argument"

def test_add_values_to_a_table():
    value_list = [{'col1': "entry4", 'col2': 4}]
    new_table = pd.DataFrame({
        'col1': ["entry1", "entry2", "entry3", "entry4"],
        'col2': [5, 10, 18, 4]
    })
    assert add_values_to_a_table(example_table, value_list).equals(new_table)

def test_prediction_ski():
    assert prediction_ski([[5]],test_table['col1'], test_table['col2']) == 10.0

def test_prediction_ski_first_argument_list_instead_of_matrix():
    assert prediction_ski([5],test_table['col1'], test_table['col2']) == "Please, provide steps argument in the form [[5]]"

def test_prediction_ski_first_argument_number_instead_of_matrix():
    assert prediction_ski(5,test_table['col1'], test_table['col2']) == "Please, provide steps argument in the form [[5]]"

def test_convert_to_grayscale():
    gray_image = np.array([[1, 1, 1, 1], [1, 1, 1, 1]])
    gray_image = np.uint8(gray_image)
    assert np.array_equal(convert_to_grayscale([test_image])[0], gray_image)

def test_rotate_images():
    rotated_image = skimage.transform.rotate(test_image, -90, resize = True, preserve_range = True)
    assert np.array_equal(rotate_images([test_image])[0], rotated_image)

def test_crop_image():
    assert crop_image(test_image, 0, 1, 0, 1).shape == (1, 1, 3)

def test_resize_images():
    smaller_image = crop_image(test_image, 0, 1, 0, 1)
    smaller_image = convert_to_grayscale([smaller_image])[0]
    gray_image = np.array([[1, 1, 1, 1], [1, 1, 1, 1]])
    gray_image = np.uint8(gray_image)
    images = resize_images([gray_image, smaller_image])
    assert images[0].shape[1] == images[1].shape[1]

def test_concatenate_images():
    smaller_image = crop_image(test_image, 0, 1, 0, 1)
    smaller_image = convert_to_grayscale([smaller_image])[0]
    gray_image = np.array([[1, 1, 1, 1], [1, 1, 1, 1]])
    gray_image = np.uint8(gray_image)
    conc_image = concatenate_images([smaller_image, gray_image])
    assert conc_image.shape == (3, 4)

def test_treshold():
    result = np.array([[[255., 255., 255.], [255., 255., 255.], [255., 255., 255.], [255., 255., 255.]],
                       [[255., 0., 0.], [255., 0., 0.], [255., 0., 0.], [255., 0., 0.]]])

    assert np.array_equal(threshold_image(test_image, 0, 0.7), result)

def test_remove_empty_elements():
    a_list = [1, 2, 3, "", 4]
    assert remove_empty_elements(a_list) == [1, 2, 3, 4]

def test_remove_empty_entries_and_swap_empty_lines_with_empty_spaces():
    a_matrix = [["", "a", "\nb", "c"], ["d\n", "e", "", "f"]]
    assert remove_empty_entries_and_lines(a_matrix) == [['a', ' b', 'c'], ['d ', 'e', 'f']]

def test_create_table():
    result_df = pd.DataFrame({'col1': ["b", "c"], 'col2': ["e", "f"]})
    a_mat = [['col1', 'b', 'c'], ['col2', 'e', 'f']]
    assert create_table(a_mat).equals(result_df)






test_replace_name()
test_replace_name_with_wrong_table_column()
test_replace_name_with_wrong_table_column_table_instead()
test_add_values_to_a_table()
test_prediction_ski()
test_prediction_ski_first_argument_list_instead_of_matrix()
test_prediction_ski_first_argument_number_instead_of_matrix()
test_convert_to_grayscale()
test_rotate_images()
test_crop_image()
test_resize_images()
test_concatenate_images()
test_treshold()
test_remove_empty_elements()
test_remove_empty_entries_and_swap_empty_lines_with_empty_spaces()
test_create_table()
