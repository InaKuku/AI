import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression

def replace_name(table, column, old_name, new_name):
    """
    Replaces values like one-floor house in the column "floors" (old_name) with an integer (new_name)
    """

    # if not isinstance(table_column, pd.Series):
    #     return "Please, provide a table column as first argument"
    table[column] = table[column].replace({old_name: new_name})

    return table


def drop_row(table, col, value):
    """
    Delets rows that contain specific value in a column
    """
    if not isinstance(col, str):
        print("Please, provide column name as string")
    if not isinstance(value, str):
        print("Please, provide the value as string")
    indices_to_remove = table[table[col].isin([value])].index
    table = table.drop(index=indices_to_remove)

    return table


list_of_no_floor_info = []
def find_floors(table):
    """
    Finds floors in the text when missing in the column; if there is no info in the text,
    fills the missing value according to house size. There is no case of missing value in col 'text'
    """
    question_mark_indices = (table[table.floors == "?"]).index

        # price_Found = False
    for ind in question_mark_indices:
        txt = table.loc[ind].text.lower()
        if "едно ниво" in txt or "един етаж" in txt or "1 етаж" in txt or "едноетаж" in txt:
            table.loc[ind, "floors"] = 1
        elif "две нива" in txt or "два етажа" in txt or "2 етажа" in txt or "двуетаж" in txt:
            table.loc[ind, "floors"] = 2
        elif "три нива" in txt or "три етажа" in txt or "3 етажа" in txt or "триетаж" in txt:
            table.loc[ind, "floors"] = 3
        elif "четири нива" in txt or "четири етажа" in txt or "4 етажа" in txt or "четириетаж" in txt:
            table.loc[ind, "floors"] = 4
        elif "първо ниво" in txt or "първи етаж" in txt or "1-ви етаж" in txt or "етаж 1" in txt:
            if "четвърто ниво" in txt or "четвърти етаж" in txt or "4-ти етаж" in txt or "етаж 4" in txt:
                table.loc[ind, "floors"] = 4
            elif "трето ниво" in txt or "трети етаж" in txt or "3-ти етаж" in txt or "етаж 3" in txt:
                table.loc[ind, "floors"] = 3
            elif "второ ниво" in txt or "втори етаж" in txt or "2-ри етаж" in txt or "етаж 2" in txt:
                table.loc[ind, "floors"] = 2
            else:
                table.loc[ind, "floors"] = 1
        else:
            #Finds the quantity of houses with unknown floors
            list_of_no_floor_info.append(ind)

            if table.loc[ind, "size"] <= 130:
                table.loc[ind, "floors"] = 1
            elif table.loc[ind, "size"] > 130:
                table.loc[ind, "floors"] = 2
            elif table.loc[ind, "size"] > 200:
                table.loc[ind, "floors"] = 3
            elif table.loc[ind, "size"] > 300:
                table.loc[ind, "floors"] = 4

    table["floors"] = table["floors"].astype(int)
    return table

def replace_floors(table):
    table = replace_name(table, "floors", "Едноетажна къща", 1)

    table = replace_name(table, "floors", "Двуетажна къща", 2)
    table = replace_name(table, "floors", "Триетажна къща", 3)
    table =replace_name(table, "floors", "Четириетажна и по-голяма", 4)

    # Delete a house-floor listings
    table = drop_row(table, "floors", 'Етаж от къща')


    #fill missing values
    quest_table = table[table["floors"] == "?"]
    if quest_table.shape[0] > 1:
        table = find_floors(table)

    return table


def remove_string(table, col):
    """
    Removes letters and tranforms the rest of the value into an integer
    """
    # if table.column.dtypes == 'object':
    if table[col].dtypes == 'object':
        str_list = (table[~table[col].str.isnumeric()]).index
        if len(str_list) > 0:
            for ind in str_list:
                val_with_letters = table.loc[ind, col]
                val = re.sub('\D', '', val_with_letters)

                table[col] = table[col].replace({val_with_letters: val})
    table[col] = table[col].astype(int)
    return table
    # return table[col].values



#sometimes agents write after price "BGN", but even in this case after that they write the same price in the text in EUR (probably a trick to get attention)

def check_string_price(table):
    """
    Checks if the price contains letters and whether they include BGN currency, if the same price is found in the text of the listing with the BGN currency,
    convert the price into EUR, if the same price in the text is in EUR, leaves it as int value. If the BGN price is missing in the text, is convertes it to EUR.
    Presumes that currencies are only EUR and BGN ('лв.', 'лева')
    """

    if table.price.dtypes == 'object':

        # Get prices with letters inside (most likely currency)
        str_indices = (table[~table.price.str.isnumeric()]).index
        for ind in str_indices:
            if type(table.loc[ind].price) == int:
                continue
            if type(table.loc[ind].price) == float:
                continue
            val_with_currency = table.loc[ind].price
            letters_list_first = list(filter(lambda x: x != " ", val_with_currency))
            letters_string_first = ''.join(letters_list_first)
            val = ""
            for symbol in letters_string_first:
                if not symbol.isalpha():
                    val = val + symbol
                else:
                    break
            if "лв" in val_with_currency or "лев" in val_with_currency:
                #A whole one_word string will be created from the text (in order to include all-kind of interval and non-interval cases)
                letters_list = list(filter(lambda x: x != " ", table.loc[ind].text))
                letters_string = ''.join(letters_list)
                letters_string = letters_string.lower()
                if val in letters_string:
                    # Index zero if the price is mentioned more than once
                    val_start_index = letters_string.find(val)
                    currency_substring_after = letters_string[val_start_index + len(val) :val_start_index + len(val) + 5]
                    currency_substring_before = letters_string[val_start_index - 5 : val_start_index]
                    if 'лв' in currency_substring_after or 'лв' in currency_substring_before or 'лев' in currency_substring_after or 'лев' in currency_substring_before \
                            or 'bgn' in currency_substring_after or 'bgn' in currency_substring_before:
                        replace_name(table, "price", table.loc[ind].price, float(float(val) * 0.51))
                    else:
                        replace_name(table, "price", table.loc[ind].price, float(val))
                else:
                    #if the price is not in the text probably is really in BGN
                    replace_name(table, "price", table.loc[ind].price, float(float(val) * 0.51))
            else:
                #If there is no BGN in the price from thw col['price'], probably is EUR
                replace_name(table, "price", table.loc[ind].price, float(val))



    table.price = table.price.astype(float)
    return table


def remove_fake_prices(table):
    """
    Removes prices that are lower than 5000 EUR
    """
    ind_to_remove = (table[table["price"] <= 1000]).index
    table = table.drop(index=ind_to_remove)
    return table


def remove_additional_listings(table):
    """
    Removes differenet listings for the same houses
    """
    table = table.reset_index(drop=True)
    new_table = table.copy(deep=True)
    ind_to_remove = []

    for row_index, a_row in table.iterrows():

            #Sets the filters
            #Makes group from the listings with the same settlement
            tb_settlement_group = table[(table['settlement'] == a_row['settlement'])]
            #size should be written as ["size"] in order to be recognized as the column
            #Separates those properties from the group with the same settlement, that have up to 4 sq. m. more size or less than the value in the a_new_table_row
            tb_size = tb_settlement_group[(a_row["size"] - 4 <= tb_settlement_group["size"]) & (tb_settlement_group["size"] <= a_row["size"] + 4)]
            #Filters out those properties from tb_size group that have more than 50sq.m in comparison with the value of the yard of the examined property or less than 50sq.m.
            tb_yard = tb_size[(a_row["yard"] - 50 <= tb_size["yard"]) & (tb_size["yard"] <= a_row["yard"] + 50)]
            # From the group with the same settlement and almost identical size and yard, separates those properties with price +/-5500 EUR
            tb_price = tb_yard[(a_row["price"] - 5500 <= tb_yard["price"]) & (tb_yard["price"] <= a_row["price"] + 5500)]

            #Doesn't include the examined listing
            filtered_table = tb_price[tb_price.index != row_index]

            #Removes repeating listings
            if filtered_table.shape[0] > 0:
                for ind in filtered_table.index:
                    ind_to_remove.append(ind)
                a = ind_to_remove
    new_table = table.drop(index=ind_to_remove)
    new_table = new_table.reset_index(drop=True)

    return new_table

def create_table(a_mat):
    """
    Generates a table on the base of a matrix
    """
    df = pd.DataFrame(a_mat)
    df = df.reset_index(drop=True)
    return df



def create_sold_selling_new_listings_tables(old_table, new_table):
    """
    Compares two tables and creates another three - of sold, still selling and new listings (old and new tables should be filtered by the additional listings beforehand)
    """
    still_selling_matrix = []
    sold_matrix = []
    for a_row_ind in range(len(old_table)):
        a_row = old_table.iloc[a_row_ind]
        #Search for still selling houses
        #set the filters by flors, +/- 2 sq.m., +/- 50 m. yard; If there are more than one responding house - it filters additionally by price
        #If there isn`t any such price in the group, looks for +/- 3000 EUR
        tb_floors = new_table[(new_table.floors == a_row.floors)]
        #size should be written as ["size"] in order to be recognized as the column
        tb_size = tb_floors[(a_row["size"] - 2 <= tb_floors["size"]) & (tb_floors["size"] <= a_row["size"] + 2)]
        tb_yard = tb_size[(a_row["yard"] - 50 <= tb_size["yard"]) & (tb_size["yard"] <= a_row["yard"] + 50)]
        # if tb_yard.shape[0] > 1:
        tb_price = tb_yard[tb_yard["price"] == a_row["price"]]
        if tb_price.shape[0] == 1:
            still_selling_matrix.append(tb_price.iloc[0])
                # still_selling_matrix.append(a_row)
        elif tb_price.shape[0] == 0:
            tb_price = tb_yard[(a_row["price"] - 10000 <= tb_yard["price"]) & (tb_yard["price"] <= a_row["price"] + 10000)]
            if tb_price.shape[0] == 1:
                still_selling_matrix.append(tb_price.iloc[0])
                a=tb_price.iloc[0]
                b=a
                    # still_selling_matrix.append(a_row)
            #Because the biggest variety in the price (necessary to catch some fall in prices) some dublicates (not caught by the filtering func) may appear here
            elif tb_price.shape[0] > 1:
                still_selling_matrix.append(tb_price.iloc[0])
            else:
                sold_matrix.append(a_row)


    still_selling_table = create_table(still_selling_matrix)
    # Finds all the listings in the new table that doesn`t exist in the still_selling_table
    new_listings_table = new_table[~new_table["price"].isin(still_selling_table["price"])]
    # dfC = dfB[dfB['A'].isin(dfA['A'].unique())]
    sold_table = create_table(sold_matrix)


    return [sold_table, still_selling_table, new_listings_table]



def make_location_into_three_columns(table):
    """
    Separates the location values into three columns - 'residential area', 'settlement' and 'region'; deletes column 'location'
    """
    residential_area = []
    settlement = []
    region = []


    table_list_col = table.copy(deep=True)
    table_list_col['location'] = table['location'].apply(lambda x: x.split(', '))
    for row_number in range(table.shape[0]):
        has_settlement = False
        has_region = False
        row = table_list_col.iloc[row_number]
        if len(row['location']) > 2:
            if len(row['location']) == 3:
                residential_area.append(row['location'][0])
                settlement.append(row['location'][1])
                region.append(row['location'][2])
            else:
                residential_area.append('0')

                #Intervals after 'село' and 'с.', etc => in order to leave out explanations like 'в центъра на селото'
                # In some locations 'село' is written twice as 'село' and as 'с.', the same with the other settlements  => if - elif

                for x in row['location']:
                    if 'село ' in x:
                        if not has_settlement:
                            settlement.append(x)
                            has_settlement = True
                    elif "с. " in x:
                        if not has_settlement:
                            settlement.append(x)
                            has_settlement = True
                    #In some cases we have two times the town, but in some cases - a village, the town nearby and the region (=> if village, elif town)
                    elif "град " in x:
                        if not has_settlement:
                            settlement.append(x)
                            has_settlement = True
                    elif "гр. " in x:
                        if not has_settlement:
                            settlement.append(x)
                            has_settlement = True
                    elif "г. " in x:
                        if not has_settlement:
                            settlement.append(x)
                            has_settlement = True

                    elif "курорт " in x:
                        if not has_settlement:
                            settlement.append(x)
                            has_settlement = True
                    elif "к.к. " in x:
                        if not has_settlement:
                            settlement.append(x)
                            has_settlement = True
                    elif "област " in x:
                        if not has_region:
                            region.append(x)
                            has_region = True
                    elif "обл. " in x:
                        if not has_region:
                            region.append(x)
                            has_region = True

                if not has_settlement:
                    ettlement.append('0')
                if not has_region:
                    region.append('0')


        else:
            if len(row['location']) == 2:
                residential_area.append('0')
                settlement.append(row['location'][0])
                region.append(row['location'][1])
            elif len(row['location']) < 2:
                table = table.drop([table.index[row.ind]])
        # if not row_number+1 == len(settlement):
        #     print(f'Row number: {row_number}, List length: {len(settlement)}')
    table_new = table.copy(deep=True)
    table_new = table_new.drop(columns='location')
    table_new['residential_area'] = np.asarray(residential_area)
    table_new['settlement'] = np.asarray(settlement)
    table_new['region'] = np.asarray(region)
    return table_new

def uniform_administration_names(table):
    """
    Swaps some administration abbreviations with the whole word, in order to make them similar to the rest of the values
    """
    table['residential_area'] = table['residential_area'].apply(lambda x: x.replace('с.', 'село'))
    table['residential_area'] = table['residential_area'].apply(lambda x: x.replace('С.', 'село'))
    table['residential_area'] = table['residential_area'].apply(lambda x: x.replace('гр.', 'град'))
    table['residential_area'] = table['residential_area'].apply(lambda x: x.replace('Гр.', 'град'))
    table['residential_area'] = table['residential_area'].apply(lambda x: x.replace('г.', 'град'))
    table['residential_area'] = table['residential_area'].apply(lambda x: x.replace('к.к.', 'курорт'))
    table['settlement'] = table['settlement'].apply(lambda x: x.replace('с.', 'село'))
    table['settlement'] = table['settlement'].apply(lambda x: x.replace('гр.', 'град'))
    table['settlement'] = table['settlement'].apply(lambda x: x.replace('г.', 'град'))
    table['settlement'] = table['settlement'].apply(lambda x: x.replace('к.к.', 'курорт'))
    table['region'] = table['region'].apply(lambda x: x.replace('обл.', 'област'))
    table['region'] = table['region'].apply(lambda x: x.replace('Обл.', 'област'))
    return table

def make_kind_of_residential_area_column(table):
    """
    Creates a column with the'residential_area' kind - center(with its kinds), neigbours, areas close to the towns and holiday-homes zones
    """

    for ind, row in table.iterrows():
        if not row["residential_area"] == str(0):
            if 'в.з.' in row["residential_area"].lower() or 'вилна зона' in row["residential_area"].lower() or 'вилна зона' in row["residential_area"].lower() or 'ризорт' in row["residential_area"].lower() or 'resort' in row["residential_area"].lower():
                table.loc[ind, 'kind_of_residential_area'] = 'holiday homes zone'
            elif 'язовир' in row["residential_area"].lower() or 'Язовир' in row["residential_area"].lower():
                table.loc[ind, 'kind_of_residential_area'] = 'holiday homes zone'
            elif 'местност' in row["residential_area"].lower():
                table.loc[ind, 'kind_of_residential_area'] = 'area close to settlement'
            elif 'център' in row["residential_area"].lower():
                table.loc[ind, 'kind_of_residential_area'] = 'center'
            else:
                table.loc[ind, 'kind_of_residential_area'] = 'neighbourhood'
        else:
            table.loc[ind, 'kind_of_residential_area'] = '0'
    return table

def make_kind_of_settlement_column(table):
    """
    Creates a column with the kinds of settlements that exist in the column 'settlement'
    """

    for ind, row in table.iterrows():
        row_region_list = row['region'].split(' ')
        region_name = row_region_list[len(row_region_list)-1]

        if 'софия' in row['settlement'].lower():
            table.loc[ind, 'kind_of_settlement'] = 'capital'
        elif 'село' in row['settlement'].lower():
            table.loc[ind, 'kind_of_settlement'] = 'village'
        #we should split region in order to take the name of the region (and we know for sure that the format there is correct)
        elif 'град' in row['settlement'].lower():
            if region_name in row['settlement']:
                table.loc[ind, 'kind_of_settlement'] = 'city'
            else:
                table.loc[ind, 'kind_of_settlement'] = 'town'
        elif 'курорт' in row['settlement'].lower() or 'к.к.' in row['settlement'].lower():
            table.loc[ind, 'kind_of_settlement'] = 'resort'
        else:
            table.loc[ind, 'kind_of_settlement'] = 'other'
    return table


def plotGraph(y_test, y_pred, regressorName):
    if max(y_test) >= max(y_pred):
        my_range = int(max(y_test))
    else:
        my_range = int(max(y_pred))
    plt.scatter(range(len(y_test)), y_test, color='blue')
    plt.scatter(range(len(y_pred)), y_pred, color='red')
    plt.legend(["actual", "predicted"], loc ="lower right")
    plt.xlabel('Observations')
    plt.ylabel('Values')
    plt.title(regressorName)
    plt.show()
    return
