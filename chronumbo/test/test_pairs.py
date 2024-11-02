from chronumbo.core.sql import (
    create_engine,
    db_to_df
)

from chronumbo.main import (
    add_event_delta_paired
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

final_kpi_paired_df = add_event_delta_paired(                   # find start, end point pairs; return df with added values
    df=df_sorted,
    col_prefix='correspondence',
    id_field=id_field,
    date_field=event_date_field,
    start_conditions={'event_type': 'Correspondence', 'is_employee': True},
    end_conditions={'event_type': 'Correspondence', 'is_employee': False},
    start_flag='start',
    end_flag='end'
)
