import numpy as np
import ipysheet
from ipysheet import sheet, cell, column, row, sheet, cell_range
import functools


def on_restr_change(change, dd_count_x_vars, dd_count_s_vars, dd_count_a_vars,
                    button_create_input_table, display_variable_input):
    with display_variable_input:
        if change['new'] != '0':
            dd_count_s_vars.options = list(map(str, range(0, int(change['new']) + 1)))
            dd_count_a_vars.options = list(map(str, range(0, int(change['new']) + 1)))
            dd_count_s_vars.layout.visibility = 'visible'
            dd_count_a_vars.layout.visibility = 'visible'
            button_create_input_table.layout.visibility = 'visible'
        else:
            # dd_count_x_vars.layout.visibility = 'hidden'
            dd_count_s_vars.layout.visibility = 'hidden'
            dd_count_a_vars.layout.visibility = 'hidden'
            button_create_input_table.layout.visibility = 'hidden'


def adjust_cj_on_basis_var_change(change, cell_table, button_start_algorithm):
    button_start_algorithm.disabled = True
    for row_id in range(2, len(cell_table)):
        if change['new'] == cell_table[row_id][1].value:
            if 's' in cell_table[row_id][1].value:
                cell_table[row_id][0].value = cell(row_id, 0, 0, read_only=True, background_color='white')
            elif 'x' in cell_table[row_id][1].value:
                cell_table[row_id][0] = cell(row_id, 0, '...', background_color='yellow')


def update_table(table, input_table, button_start_algorithm):
    # on change of input_table the table needs to be checked again
    input_table = table['new']
    button_start_algorithm.disabled = True


def check_correct_input(button, button_start_algorithm, cell_table, input_table):
    wrong_input_counter = 0

    # check if input is a number
    for row_id in range(0, len(cell_table)):
        for column_id in range(0, len(cell_table[0])):
            if cell_table[row_id][column_id].style == {'backgroundColor': 'yellow'} or \
                    cell_table[row_id][column_id].style == {'backgroundColor': 'red'} and column_id != 1:
                try:
                    test = float(cell_table[row_id][column_id].value)
                    cell_table[row_id][column_id].style = {'backgroundColor': 'yellow'}
                except ValueError:
                    cell_table[row_id][column_id].style = {'backgroundColor': 'red'}
                    wrong_input_counter += 1

    # check column of basis variables
    df_tableau = ipysheet.to_dataframe(input_table)
    for column_id, var in enumerate(df_tableau.iloc[1, 3:], 3):
        for row_id, basis_var in enumerate(df_tableau.iloc[2:, 1], 2):
            if var == basis_var:
                count_var_values = df_tableau.iloc[2:, column_id].value_counts()
                if list(count_var_values.index) == ['0', '1']  or list(count_var_values.index) == ['1']:
                    if int(df_tableau.iloc[row_id, column_id]) == 1 and count_var_values['1'] == 1:
                        if '0' in count_var_values.index:
                            if count_var_values['0'] == len(df_tableau.iloc[2:, 1]) - 1:
                                continue
                        else:
                            continue

                for row in range(2, len(cell_table)):
                    cell_table[row][column_id].style = {'backgroundColor': 'red'}
                wrong_input_counter += 1

    # manage visibility of button which start simplex algorithm
    if wrong_input_counter == 0:
        button_start_algorithm.disabled = False
    else:
        button_start_algorithm.disabled = True


def add_missing_cj_and_cj_zj_rows(tableau, M):
    zj = []
    cj_zj = []
    
    #create zj and cj_zj row
    for column_id in range(0, len(tableau.columns)):
        if column_id == 0:
            zj.append(np.nan)
            cj_zj.append(np.nan)
        elif column_id == 1:
            zj.append('zj')
            cj_zj.append('cj-zj')
        elif column_id == 2:
            zj.append(0)
            cj_zj.append(np.nan)
        else:
            zj.append(0)
            cj_zj.append(0)

    #add rows to tableau
    tableau.loc[len(tableau.index)] = zj
    tableau.loc[len(tableau.index)] = cj_zj
    tableau.replace('-M', -M, inplace=True)

    # change input to float if possible
    for row_id in tableau.index:
        for column_id in tableau.columns:
            try:
                tableau.loc[row_id][column_id] = float(tableau.loc[row_id][column_id])
            except:
                pass

    return tableau


def prefill_tableau_text_and_colour(input_table, dd_count_restr, dd_count_x_vars,
                                    dd_count_s_vars, dd_count_a_vars, button_start_algorithm, M):
    variables = []
    column_id_counter = 3  # start at 3 because there the informations of the restrictions are written
    row_basis_var = 2

    # zwei Dimensionales Array, welches Sheet repräsentiert
    cell_table = [[0] * input_table.columns for i in range(input_table.rows)]

    for row_id in range(0, input_table.rows):
        for column_id in range(0, input_table.columns):
            if column_id != 0 and column_id != 1:
                cell_table[row_id][column_id] = cell(row_id, column_id, '...', background_color='yellow')
                cell_table[row_id][column_id].observe(functools.partial(update_table, input_table=input_table,
                                                                        button_start_algorithm=button_start_algorithm))

    cell_table[0][0] = cell(0, 0, '', read_only=True, background_color='grey')
    cell_table[0][1] = cell(0, 1, '', read_only=True, background_color='grey')
    cell_table[0][2] = cell(0, 2, '', read_only=True, background_color='grey')

    # Befülle row mit Beschreibung
    cell_table[1][0] = cell(1, 0, 'cj', read_only=True, font_weight='bold', background_color='white')
    cell_table[1][1] = cell(1, 1, 'Basisvariable', read_only=True, font_weight='bold', background_color='white')
    cell_table[1][2] = cell(1, 2, 'Quantity', read_only=True, font_weight='bold', background_color='white')

    for anz in range(1, int(dd_count_x_vars.value) + 1):
        var_name = 'x' + str(anz)
        cell_table[1][column_id_counter] = cell(1, column_id_counter, var_name, read_only=True,
                                                font_weight='bold', background_color='white')
        variables.append(cell_table[1][column_id_counter])
        column_id_counter += 1

    for anz in range(1, int(dd_count_s_vars.value) + 1):
        var_name = 's' + str(anz)
        cell_table[0][column_id_counter] = cell(0, column_id_counter, 0, read_only=True, background_color='white')
        cell_table[1][column_id_counter] = cell(1, column_id_counter, var_name, read_only=True,
                                                font_weight='bold', background_color='white')
        variables.append(cell_table[1][column_id_counter])
        column_id_counter += 1

    for anz in range(1, int(dd_count_a_vars.value) + 1):
        var_name = 'a' + str(anz)
        cell_table[0][column_id_counter] = cell(0, column_id_counter, '-M', read_only=True, background_color='white')
        cell_table[1][column_id_counter] = cell(1, column_id_counter, var_name, read_only=True,
                                                font_weight='bold', background_color='white')
        variables.append(cell_table[1][column_id_counter])
        column_id_counter += 1

    start_basisvar = variables[(len(variables) - int(dd_count_restr.value)):]
    start_basisvar.sort(key=lambda x: x.value)
    basis_selection = []

    for var in variables:
        if 'a' in var.value:
            break
        basis_selection.append(var.value)

    for row_id in range(2, input_table.rows):
        if 'a' in start_basisvar[row_id - 2].value:
            cell_table[row_id][0] = cell(row_id, 0, '-M', read_only=True, background_color='white')
            cell_table[row_id][1] = cell(row_id, 1, start_basisvar[row_id - 2].value, read_only=True,
                                         font_weight='bold', background_color='white')
        if 's' in start_basisvar[row_id - 2].value:
            cell_table[row_id][0] = cell(row_id, 0, 0, read_only=True, background_color='white')
            cell_table[row_id][1] = cell(row_id, 1, start_basisvar[row_id - 2].value, read_only=False,
                                         font_weight='bold', choice=basis_selection, background_color='yellow')
            cell_table[row_id][1].observe(functools.partial(adjust_cj_on_basis_var_change, cell_table=cell_table,
                                                            button_start_algorithm=button_start_algorithm))
        if 'x' in start_basisvar[row_id - 2].value:
            cell_table[row_id][1] = cell(row_id, 1, start_basisvar[row_id - 2].value, read_only=False,
                                         font_weight='bold', choice=basis_selection, background_color='yellow')
            cell_table[row_id][0] = cell(row_id, 0, '...', background_color='yellow')
            cell_table[row_id][1].observe(functools.partial(adjust_cj_on_basis_var_change, cell_table=cell_table,
                                                            button_start_algorithm=button_start_algorithm))

    return input_table, cell_table
