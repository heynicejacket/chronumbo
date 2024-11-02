from chronodetective.core.sql import (
    create_engine,
    db_to_df
)

from chronodetective.main import (
    add_event_delta_single
)


# ===== example variables ============================================================================================

verbose = True

db = ''
dialect = 'postgres'
user = ''
password = ''
endpoint = ''

event_date_field = 'event_date'
id_field = 'project_id'

audit_query = """
    SELECT
        t1.project_id,
        t1.event_date,
        t1.event_type,
        t1.event_description,
        t2.employee_alias,
        COALESCE(t2.alias IS NOT NULL, 'False') AS is_employee
    FROM project_audit_trail AS t1
    LEFT JOIN employees AS t2 ON t1.employee_alias = t2.alias
"""


# ===== example usage ================================================================================================

engine = create_engine(                                         # create SQL connection engine
    db=db,
    dialect=dialect,
    user=user,
    password=password,
    endpoint=endpoint,
    mssql_driver=17,
    fast_executemany=False,
    verbose=verbose
)

df = db_to_df(                                                  # create test DataFrame from SQL query
    query=audit_query,
    engine=engine,
    verbose=verbose
)

# df[event_date_field] = pd.to_datetime(df[event_date_field])   # date field must be datetime
df_sorted = df.sort_values(by=[id_field, event_date_field])     # sort by IDs and date

final_kpi_single_df = add_event_delta_single(                   # find start, end point pair; return df with added values
    df=df_sorted,
    col_prefix='project_res_time',
    id_field=id_field,
    date_field=event_date_field,
    start_conditions={'event_type': 'Status', 'event_description': 'Created'},
    end_conditions={'event_type': 'Status', 'event_description': 'Resolved'},
    start_flag='start',
    end_flag='end',
    end_at_latest=False,                                        # stop time delta at first end condition
    use_earliest_if_no_start=True,                              # if no start condition, True starts at first entry per ID
    use_latest_if_no_end=True                                   # if no end condition, False does not calculate delta
)
