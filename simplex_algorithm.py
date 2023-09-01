import pandas as pd
import numpy as np
import copy
import sympy as sp


def simplex_algorithm(tableau, max_iterations, infinite):
    tableau = tableau.copy()
    number_of_rows = len(tableau.index)
    counter_iterations = 0  # counter to stop infinite loop
    is_solution_found = False  # check if end solution is found
    messages = []  # list of error messages
    pivot_elements_ids = []  # [[pivot_row0, pivot_column0], ...]
    tableaus = [copy.deepcopy(tableau.fillna(''))]  # list of all tableaus

    # continue as long as cj-zj has at least one positive value
    while get_max_cj_zj(tableau, infinite) > 0:
        messages.append([])  # messages for current iteration

        # get pivot row and column
        pivot_column_id = get_pivot_column_id(tableau, infinite)
        pivot_row_id = get_pivot_row_id(tableau, pivot_column_id, number_of_rows)
        pivot_elements_ids.append([pivot_row_id, pivot_column_id])

        if check_unlimited_solution_space(pivot_row_id, messages[counter_iterations]):
            break

        # update simplex 
        update_simplex_tableau(tableau, pivot_row_id, pivot_column_id, number_of_rows)
        tableau = calculate_cj_and_cj_zj(tableau)
        tableau = tableau.fillna('')  # alle unnötigen Felder werden geleert
        tableaus.append(copy.deepcopy(tableau))  # füge das neue Tableau wieder in die Liste hinzu

        counter_iterations += 1
        if counter_iterations == max_iterations:
            break

    # check what was the condition to leave loop
    if get_max_cj_zj(tableau, infinite) <= 0:
        is_solution_found = True

    # informations for final tableau
    messages.append([])
    pivot_elements_ids.append([None, None])

    check_infeasibility(tableaus[-1], messages[-1], is_solution_found)

    return tableaus, messages, pivot_elements_ids


# calculate maximal cj-zj value
def get_max_cj_zj(tableau, infinite):
    copy_tableau = copy.deepcopy(tableau)

    # control every column except the first two
    for column in copy_tableau:
        if column != 0 and column != 1 and column != 2:
            # replace mathematical symbol with big number to represent infinity
            if isinstance(copy_tableau.iloc[-1, column], sp.Expr):
                copy_tableau.iloc[-1, column] = copy_tableau.iloc[-1, column].subs(infinite, 9999)
            try:
                # change, if not yet, cj-zj to float
                copy_tableau.iloc[-1, column] = float(copy_tableau.iloc[-1, column])
            except:
                pass

    max_value = copy_tableau.iloc[-1, 3:].max(axis=0)
    return max_value


def get_pivot_column_id(tableau, infinite):
    # make copy
    copy_tableau = copy.deepcopy(tableau)

    # loop over columns
    for column in copy_tableau:
        # nur Zeilen mit Ressourcenverbrauchskoeffizienten werden angesehen
        if column != 0 and column != 1 and column != 2:
            # replace mathematical placeholder -M with a big number to representate infinite
            if isinstance(copy_tableau.iloc[-1, column], sp.Basic):
                copy_tableau.iloc[-1, column] = copy_tableau.iloc[-1, column].subs(infinite, 9999)
            copy_tableau.iloc[-1, column] = int(copy_tableau.iloc[-1, column])

    # get id of biggest cj-zj value
    pivot_column_id = copy_tableau.iloc[-1, 3:].astype(float).idxmax(axis=0)
    return pivot_column_id


def get_pivot_row_id(tableau, pivot_column_id, number_of_rows):
    # make copy
    copy_tableau = copy.deepcopy(tableau)

    # get values of pivot column and quantity of basis variables
    pivot_column_values = copy_tableau.iloc[copy_tableau.index.difference([0, 1, (number_of_rows - 1),
                                                                           (number_of_rows - 2)]), pivot_column_id]
    quantity = copy_tableau.iloc[copy_tableau.index.difference([0, 1, (number_of_rows - 1), (number_of_rows - 2)]), 2]

    # prevent division by 0
    pivot_column_values.mask(pivot_column_values <= 0, np.nan, inplace=True)
    # supporting matrix for decision making
    deciding_values = quantity / pivot_column_values
    # id with smalles value gets selected as pivot row
    pivot_row_id = deciding_values.astype(float).idxmin(skipna=True)
    return pivot_row_id


# -----------------------------------------------------------------------------

def update_simplex_tableau(tableau, pivot_row_id, pivot_column_id, number_of_rows):
    # pivot row gets divided by pivot element value to get pivotelement to value 1
    tableau.iloc[pivot_row_id, 2:] = tableau.iloc[pivot_row_id, 2:] / tableau.iloc[pivot_row_id, pivot_column_id]

    # exchange basis variable info (cj and variable name)
    tableau = update_pivot_row(tableau, pivot_row_id, pivot_column_id)
    # update remaining rows which represent restrictions
    tableau = update_basis_variables(tableau, pivot_row_id, pivot_column_id, number_of_rows)
    return tableau


def update_pivot_row(tableau, old_basis_var, new_basis_var):
    # update cj value of pivot row
    tableau.iloc[old_basis_var, 0] = tableau.iloc[0, new_basis_var]
    # update variable name of pivot row
    tableau.iloc[old_basis_var, 1] = tableau.iloc[1, new_basis_var]
    return tableau


def update_basis_variables(tableau, pivot_row_id, pivot_column_id, number_of_rows):
    for index in tableau.index:
        # update remaining rows so the pivot columns value becomes 0 zero for these rows
        if index != pivot_row_id and index not in [0, 1, number_of_rows - 1, number_of_rows - 2]:
            # row_values = row_values - pivot_row_values * pivot_column_element  
            tableau.iloc[index, tableau.columns.difference([0, 1], sort=False)] = \
                tableau.iloc[index, tableau.columns.difference([0, 1], sort=False)] - \
                ((tableau.iloc[pivot_row_id, tableau.columns.difference([0, 1], sort=False)] *
                  tableau.iloc[index, pivot_column_id]))

    return tableau


# ----------------------------------------------------------------------------
def calculate_cj_and_cj_zj(tableau):
    number_of_rows = len(tableau.index)
    # calcuclate zj row
    for column_id in range(0, len(tableau.columns)):
        if column_id != 0 and column_id != 1:
            # zj= sum(cj_of_basis_variables * column_values) 
            cj_basis_var = tableau.iloc[tableau.index.difference([0, 1, number_of_rows - 1, number_of_rows - 2],
                                                                 sort=False), 0]
            column_values = tableau.iloc[tableau.index.difference([0, 1, number_of_rows - 1, number_of_rows - 2],
                                                                  sort=False), column_id]
            tableau.iloc[-2, column_id] = (cj_basis_var * column_values).sum()

            # if possible change sympy-format to float in cj-zj row
            for id_column in range(0, len(tableau.columns)):
                if isinstance(tableau.iloc[-2, id_column], sp.Expr):
                    try:
                        tableau.iloc[-2, id_column] = float(tableau.iloc[-2, id_column])
                    except:
                        pass

                # round float to two decimal digits in cj-zj row for artifical variables
                if isinstance(tableau.iloc[-2, id_column], float) and \
                        isinstance(tableau.iloc[0, id_column], sp.core.mul.Mul):
                    tableau.iloc[-2, id_column] = round(tableau.iloc[-2, id_column], 2)

    # calcucalte cj-zj row
    tableau.iloc[-1, tableau.columns.difference([0, 1, 2], sort=False)] = \
        tableau.iloc[0, tableau.columns.difference([0, 1, 2], sort=False)] - \
        tableau.iloc[-2, tableau.columns.difference([0, 1, 2], sort=False)]
    return tableau


# check for infeasibility
def check_infeasibility(last_tableau, message, is_solution_found):
    # if a artifical variable is in the final solution, the problem is infeasible
    # the mathematical symbol would be in zj of the quantity
    if isinstance(last_tableau.iloc[-2, 2], sp.Basic) and is_solution_found == True:
        message.append('Spezialfall: Unausführbarkeit (Infeasibility) -> Falls ein optimales Tableau eine ' \
                       'künstliche Variable enthält, ist das Problem unlösbar („infeasible“).')


# check for unlimited solution space
def check_unlimited_solution_space(pivot_row_id, message):
    # if no pivot_row_id was found, the problem has unlimited solution space
    if np.isnan(pivot_row_id):
        message.append('Spezialfall: unbeschränkter Lösungsraum -> keine zulässige Pivotzeile ' \
                       '=> Lösungsraum unbeschränkt.')
        return True
    else:
        return False

