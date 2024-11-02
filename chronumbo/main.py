def _check_conditions(row, conditions):
    """
    Helper function to check if all specified conditions are met for a given row.

    This function iterates through provided conditions (a dictionary of field-value pairs) and checks if corresponding
    fields in row match specified values. If all conditions met, returns True; otherwise, returns False.

    _check_conditions performs as follows:

        row = pd.Series({'event': 'Status', 'description': 'Created'})

        conditions = {'event': 'Status', 'description': 'Created'}
        _check_conditions(row, conditions)                                      # conditions met, returns True

        conditions = {'event': 'Correspondence', 'description': 'Updated'}
        _check_conditions(row, conditions)                                      # conditions not met, returns False

    :param row:                 series, required        pandas Series, each element corresponding to field in DataFrame
    :param conditions:          dict, required          dict of column names and expected values
    :return:                    bool                    True if all conditions are met; else False
    """

    return all(row[field] == value for field, value in conditions.items())


def _update_start(df, idx, row, start_col, start_flag, date_field, start_at_earliest, start_time):
    """
    Helper function to update the start column and track start time based on specified conditions.

    This function sets start time for event by updating start column in DataFrame and tracking time in 'start_time'
    variable. The function behaves differently based on 'start_at_earliest' flag:

        - if start_at_earliest=True, updates start time for first occurrence
        - if start_at_earliest=False, updates start time for latest occurrence where end_time is None

    :param df:                  df, required            DataFrame being updated with start information
    :param idx:                 int, required           index of current row in DataFrame
    :param row:                 series, required        current row being processed
    :param start_col:           str, required           name of start column in DataFrame to be updated
    :param start_flag:          str, required           flag to assign to start column
    :param date_field:          str, required           name of column containing event date or timestamp
    :param start_at_earliest:   bool, required          flag to capture earliest (True) or latest (False)
    :param start_time:          datetime, required      start time being tracked, updated when valid condition met
    :return:                    datetime                updated start time, reflecting time captured based on conditions
    """

    if start_at_earliest and start_time is None:
        start_time = row[date_field]
        df.at[idx, start_col] = start_flag
    elif not start_at_earliest:
        start_time = row[date_field]
        df.at[idx, start_col] = start_flag
    return start_time


def _update_end(df, idx, row, end_col, end_flag, date_field, end_at_latest, end_time):
    """
    Helper function to update the end column and track the end time based on the specified conditions.

    This helper function sets end time for event by updating end column in DataFrame and tracking time in end_time
    variable. The function behaves differently based on end_at_latest flag:

        - if end_at_latest=True, updates end time for latest occurrence
        - if end_at_latest=False, updates end time for earliest occurrence where end_time is None

    :param df:                  df, required            DataFrame being updated with end information
    :param idx:                 int, required           index of current row in DataFrame
    :param row:                 series, required        current row being processed
    :param end_col:             str, required           name of end column in DataFrame to be updated
    :param end_flag:            str, required           flag to assign to end column
    :param date_field:          str, required           name of column containing event date or timestamp
    :param end_at_latest:       bool, required          flag to capture latest end time (True) or earliest (False)
    :param end_time:            datetime, required      end time being tracked, updated when valid condition met
    :return:                    datetime                updated end time, reflecting time captured based on conditions
    """

    if end_at_latest:
        end_time = row[date_field]
        df.at[idx, end_col] = end_flag
    elif not end_at_latest and end_time is None:
        end_time = row[date_field]
        df.at[idx, end_col] = end_flag
    return end_time


def _handle_no_start(df, group, date_field, start_col, start_na_flag, use_earliest_if_no_start):
    """
    Helper function to handle cases when no start condition is met, by assigning the earliest date in the group. If
    use_earliest_if_no_start flag set to True, it assigns earliest event date in group to start column and marks it
    with start_na_flag.

    Returns either the earliest start time, or None if the flag is set to not use the earliest date.

    :param df:                          df, required            DataFrame being updated with start information
    :param group:                       str, required           group of rows corresponding to current id_field value
    :param date_field:                  str, required           name of column containing event date or timestamp
    :param start_col:                   str, required           name of start column in DataFrame to be updated
    :param start_na_flag:               str, required           flag to assign to start column when no start condition met
    :param use_earliest_if_no_start:    bool, required          flag to use earliest date in group if no start condition met
    :return:                            datetime or None        earliest start time or None
    """

    if use_earliest_if_no_start:
        earliest_idx = group[date_field].idxmin()
        start_time = group.loc[earliest_idx, date_field]
        df.at[earliest_idx, start_col] = start_na_flag
        return start_time
    return None


def _handle_no_end(df, group, date_field, end_col, end_na_flag, use_latest_if_no_end):
    """
    Helper function to handle cases when no end condition is met, by assigning the latest date in the group. If
    use_latest_if_no_end flag set to True, it assigns the latest event date in group to end column and marks it with
    the end_na_flag.

    Returns either the latest end time and the index of the row in question, or None (end_time) if flag set to not use
    latest date, and None (latest_idx) if no end condition is met.

    :param df:                          df, required            DataFrame being updated with start information
    :param group:                       str, required           group of rows corresponding to current id_field value
    :param date_field:                  str, required           name of column containing event date or timestamp
    :param end_col:                     str, required           name of end column in DataFrame to be updated
    :param end_na_flag:                 str, required           flag to assign to end column when no end condition met
    :param use_latest_if_no_end:        bool, required          flag to use latest date in group if no end condition met
    :return end_time:                   datetime or None        latest end time, or None
            latest_idx:                 int or none             row index of latest event in group, or None
    """

    if use_latest_if_no_end:
        latest_idx = group[date_field].idxmax()
        end_time = group.loc[latest_idx, date_field]
        df.at[latest_idx, end_col] = end_na_flag
        return end_time, latest_idx
    return None, None


def add_event_delta_single(df, col_prefix, id_field, date_field, start_conditions, end_conditions,
                           start_flag='start', end_flag='end', start_na_flag='start-na', end_na_flag='end-na',
                           start_at_earliest=True, end_at_latest=True, use_earliest_if_no_start=False,
                           use_latest_if_no_end=False):
    """
    Given an audit trail DataFrame (see below for definition of "audit trail"), adds columns to DataFrame to calculate
    time delta between specific start and end events for each group, defined by an identifier field (e.g. project_no).

    The function tracks start and end events based on a dictionary of conditions, marks them with labels identifying
    then as such, and calculates time delta between start and end of event.

    By default, the function looks for earliest start and latest end of given criteria. Given a DataFrame and default
    parameters, if looking for the delta between correspondence and project resolution, as follows:

        case_id   event_date            event           description    start    end
        --------  --------------------  --------------  -------------  -------  -----
        100041    2023-09-27 22:54:41   Status          Created
        100041    2023-09-29 17:04:22   Correspondence  Updated        start            <-- if first start condition
        100041    2023-09-30 17:04:22   Assigned        mrunde
        100041    2023-10-01 15:13:18   Correspondence  Updated        start            <-- if latest start condition
        100041    2023-10-01 20:44:45   Status          Resolved                end     <-- if first end condition
        100041    2023-10-16 17:04:22   Assigned        fstein
        100041    2023-12-04 19:58:08   Status          Resolved                end     <-- if latest end condition

    If conditions are missing, by default there will be no start and/or end, and no calculation will take place. If
    use_earliest_if_no_start or use_latest_if_no_end are set to True, the earliest and latest dates will be used as
    assumed start or end points.

    If the metric to be measured is the time from a project's start to completion, and the project management system
    normally produces 'Created' as the start of a project, and 'Resolved' as the end of a project, if the audit trail
    of a given project does not have these events, it may be assumed that the earliest and latest events in the
    project's audit trail might stand in, as follows:

        case_id   event_date            event           description    start      end
        --------  --------------------  --------------  -------------  ---------  -----
        100041    2023-09-27 22:54:41   Status          Pending Order  start-na         <-- first event, assumed start
        100041    2023-09-29 17:04:22   Correspondence  Updated
        100041    2023-09-30 17:04:22   Assigned        mrunde
        100041    2023-10-01 15:13:18   Correspondence  Updated
        100041    2023-10-01 20:44:45   Status          On Hold
        100041    2023-10-16 17:04:22   Assigned        fstein
        100041    2023-12-04 19:58:08   Status          Ordered                   end-na  <-- latest event, assumed end

    end event (or based on user-defined criteria). Optionally, if no matching conditions are found, the earliest date
    for start and latest date for end can be used, with 'start-na' and 'end-na' flags.

    :param df:                          df, required        DataFrame containing event data
    :param col_prefix:                  str, required       prefix for new column names that will be added to DataFrame
    :param id_field:                    str, required       column name used to group data (e.g. 'project_no')
    :param date_field:                  str, required       column containing datetime used to calculate time delta
    :param start_conditions:            dict, required      dict specifying conditions for identifying start event
    :param end_conditions:              dict, required      dict specifying conditions for identifying end event
    :param start_flag:                  str, optional       label to mark start event in new start column
    :param end_flag:                    str, optional       label to mark end event in new end column
    :param start_na_flag:               str, optional       label to mark start event if no matching start condition found
    :param end_na_flag:                 str, optional       label to mark end event if no matching end condition found
    :param start_at_earliest:           bool, optional      if True, marks first start event within each group
    :param end_at_latest:               bool, optional      if True, marks last end event within each group
    :param use_earliest_if_no_start:    bool, optional      if True, uses earliest date in group if no matching condition
    :param use_latest_if_no_end:        bool, optional      if True, uses latest date in group if no matching condition
    :return:                            df                  input DataFrame with new flag and delta columns
    """

    start_col = f'{col_prefix}_start'
    end_col = f'{col_prefix}_end'
    delta_col = f'{col_prefix}_delta'
    delta_sec_col = f'{col_prefix}_delta_sec'

    df[[start_col, end_col, delta_col, delta_sec_col]] = None

    # group by id_field to handle each group separately
    for case_id, group in df.groupby(id_field):
        start_time, end_time = None, None
        start_row_idx, end_row_idx = None, None
        latest_idx = None

        # iterate through each row in group
        for idx, row in group.iterrows():

            # check for start conditions
            if _check_conditions(row, start_conditions):
                start_time = _update_start(df, idx, row, start_col, start_flag, date_field, start_at_earliest, start_time)

            # check for end conditions
            elif _check_conditions(row, end_conditions):
                end_time = _update_end(df, idx, row, end_col, end_flag, date_field, end_at_latest, end_time)
                end_row_idx = idx

        # handle case when no start condition is found
        if start_time is None:
            start_time = _handle_no_start(df, group, date_field, start_col, start_na_flag, use_earliest_if_no_start)

        # handle case when no end condition is found
        if end_time is None:
            end_time, latest_idx = _handle_no_end(df, group, date_field, end_col, end_na_flag, use_latest_if_no_end)

        # calculate delta and delta_sec only at point where 'end' or 'end-na' is marked
        if start_time and end_time:

            # if valid end condition
            if end_row_idx is not None:
                delta = end_time - start_time
                df.at[end_row_idx, delta_col] = str(delta)
                df.at[end_row_idx, delta_sec_col] = delta.total_seconds()

            # if 'end-na' is marked
            elif latest_idx is not None:
                delta = end_time - start_time
                df.at[latest_idx, delta_col] = str(delta)
                df.at[latest_idx, delta_sec_col] = delta.total_seconds()

    return df


def add_event_delta_paired(df, col_prefix, id_field, date_field, start_conditions, end_conditions, start_flag='start',
                          end_flag='end'):
    """
    Calculates deltas for every start-end point pair within a given id_field based on specified conditions.

    For each id_field group, this function will find all rows matching start conditions and all rows matching end
    conditions. These are then paired, and the delta is calculated for each pair of start point with the next available
    end point.

    The function tracks pairs of start and end events based on a dictionary of conditions, marks them with labels
    identifying then as such, and calculates time delta between start and end of event.

    Given a DataFrame and default parameters, if looking for the delta between employee and customer correspondence,
    as follows:

        case_id   event_date            event           is_employee    start    end
        --------  --------------------  --------------  -------------  -------  -----
        100041    2023-09-27 22:54:41   Status          Created
        100041    2023-09-29 17:04:22   Correspondence  True           start            <-- start condition
        100041    2023-09-30 17:04:22   Correspondence  True
        100041    2023-10-01 15:13:18   Correspondence  False                   end     <-- end condition
        100041    2023-10-01 20:44:45   Correspondence  False
        100041    2023-10-16 17:04:22   Correspondence  False
        100041    2023-10-19 21:13:01   Correspondence  True           start            <-- start condition
        100041    2023-10-24 19:23:44   Correspondence  True
        100041    2023-12-03 23:28:19   Correspondence  False                   end     <-- end condition

    :param df:                  df, required        DataFrame containing event data
    :param col_prefix:          str, required       prefix for new column names that will be added to DataFrame
    :param id_field:            str, required       column name used to group data (e.g. 'project_no')
    :param date_field:          str, required       column containing datetime used to calculate time delta
    :param start_conditions:    dict, required      dict specifying conditions for identifying start event
    :param end_conditions:      dict, required      dict specifying conditions for identifying end event
    :param start_flag:          str, optional       label to mark start event in new start column
    :param end_flag:            str, optional       label to mark end event in new end column
    :return:                    df                  input DataFrame with new flag and delta columns
    """

    delta_col = f'{col_prefix}_delta'
    delta_sec_col = f'{col_prefix}_delta_sec'

    # initialize new columns with None
    df[[delta_col, delta_sec_col]] = None

    # group by id_field to handle each group separately
    for case_id, group in df.groupby(id_field):
        start_time = None
        start_idx = None

        # iterate through each row in the group
        for idx, row in group.iterrows():
            # check for start condition
            if start_time is None and _check_conditions(row, start_conditions):
                start_time = row[date_field]
                start_idx = idx

                # mark start event
                df.at[start_idx, delta_col] = start_flag

            # check for end condition after start is found
            elif start_time is not None and _check_conditions(row, end_conditions):
                end_time = row[date_field]
                delta = end_time - start_time
                delta_seconds = delta.total_seconds()

                # mark end event and calculate delta
                df.at[idx, delta_col] = end_flag
                df.at[idx, delta_sec_col] = delta_seconds

                # reset for next start-end pair
                start_time = None
                start_idx = None

    return df
