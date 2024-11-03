![chronumbo](https://github.com/heynicejacket/chronumbo/blob/master/chronumbo-banner.png)

There were too many github repos named "timecop", and when providing reporting to clients, there's always just one more thing.

# chronumbo

## Why?

In reporting on KPIs and other project management metrics, internally and to clients, it is common to report trends, histograms, and averages of durations between project phases or other tasks. This repo provides a single-function to intake a DataFrame and conditions to track start and end points, and report time deltas back to the user.

`chronumbo` comes in two flavours:

* `add_event_delta_single()` to track time between two events, commonly project phases
* `add_event_delta_pairs()` to track time between multiple pairs of events, for recurring actions

## Some basic terminology

While some terminology is fairly universal, many terms are infinitely varied across different industries, companies, and corporate cultures. For the purposes of this project, we'll define here a few placeholder terms.

* **Project** - these sorts of asks can be for projects, services, orders, bugs, etc.; for simplicity's sake, I will refer to these generically as "projects". While the particulars of these differ widely, the collection of data is broadly the same.
* **Current State Table** - a table which generally has one row per project, with the latest data for that project (e.g. current status, current assignee, etc.).
* **Event Log Table** - a table which has one row per event, and many rows per project.
* **Project ID** - the unique identifier for the Current State Table.
* **Event ID** - the unique identifier for rows in the Event Log Table.

### Example datasets

The test dataset `../chronumbo/test/project-event-log.csv` represents an Event Log table, and contains the following fields:

![ project_id | event_date | event | description | alias | is_employee |](https://github.com/heynicejacket/chronumbo/blob/master/chronumbo-test-csv-headers.png)

Event logs produced by most tools will have a similar structure, and is fairly straightforward data structure to replicate for those tools that do not produce such logs explicitly (e.g. Google Sheets, Smartsheet, etc.).

## Basic implentation

The most basic implementation is simply calling either `add_event_delta_single()` or `add_event_delta_pairs()` with the following general logic:

* `df` a DataFrame containing Event Log, ordered by ID and date
* `id_field` the Project ID in the Event Log
* `event_date_field` the event date field in the Event Log
* `start_conditions` dictionary containing key-value pairs of fields and values marking the start point
* `end_conditions` dictionary containing key-value pairs of fields and values marking the end point
* `start_at_earliest` if True, starts at the first instance of start condition
* `end_at_latest` if True, ends at the latest instance of end condition
* `use_earliest_if_no_start` if True, start at first event in log if no matching start condition*
* `use_latest_if_no_end` if True, end at last event in log if no matching end condition*

🚨 _See [Issue #3](https://github.com/heynicejacket/chronumbo/issues/3); currently, `add_event_delta_pairs()` has no `use_earliest_if_no_start` or `use_latest_if_no_end` parameters. This function looks for multiple sets, and was initially designed for that purpose explicitly. There will be cases where the user will want to use the earliest and latest event dates to start or end a pair. This will be added._

You can feed a DataFrame into either on your own, but for the less tech-savvy (and the lazy), I've included in this project the following functions to get you going with minimal work. See **Additional helper functions** below for more information.

```
# create SQLAlchemy connection engine
engine = create_engine(
    db=db,
    dialect=dialect,
    user=user,
    password=password,
    endpoint=endpoint,
    verbose=verbose
)

# create DataFrame from SQL query
df = db_to_df(
    query=audit_query,
    engine=engine,
    verbose=verbose
)
```

Your DataFrame will need to be sorted:

```
# sort by IDs and date
df_sorted = df.sort_values(by=[id_field, event_date_field])
```

For `both add_event_delta_single()` and `add_event_delta_pairs()`, given `col_prefix='project_res_time'`, the input DataFrame is returned with four additional fields:

* `project_res_time_start` a flag indicating the start point; for debugging and reporting
* `project_res_time_end` a flag indicating the end point; for debugging and reporting
* `project_res_time_delta` returns a string version of time delta, e.g. '0 days 01:30:00'
* `project_res_time_delta_sec` returns time delta as seconds, e.g. 5400.0

🚨 _See [Issue #4](https://github.com/heynicejacket/chronumbo/issues/4); it may be best to include optional sorting inside the function. This may be added in the future._

### add_event_delta_single()
<center>![chronumbo single pair](https://github.com/heynicejacket/chronumbo/blob/master/chronumbo-single-pair.png)</center>

To find the time delta between a single starting event and a single ending event, use `add_event_delta_single()`. This is useful in determining the time it takes for a project to be completed, or between stages of a project.

Below, the example function looks for where the Status field lists "Created" as the start point for calculating a time delta, and where the Status field lists "Resolved" as the end point.

```
# find start, end point pair; return df with added values
final_kpi_single_df = add_event_delta_single(
    df=df_sorted,
    col_prefix='project_res_time',
    id_field=id_field,
    date_field=event_date_field,
    start_conditions={'event': 'Status', 'description': 'Created'},
    end_conditions={'event': 'Status', 'description': 'Resolved'},
    start_flag='start',
    end_flag='end',
    end_at_latest=False,
    use_earliest_if_no_start=True,
    use_latest_if_no_end=True
)
```

### add_event_delta_pairs()
<center>![chronumbo multi pair](https://github.com/heynicejacket/chronumbo/blob/master/chronumbo-multi-pair.png)</center>

To find each time delta between a series of start and end events, use `add_event_delta_pairs()`. This is useful in determining the average time of recurring events, like responding to customer correspondence and project manager's response.

Below, the example function looks for where a non-employee sends a message in the project management system, and when an employee responds. Once the end condition has been met, the function looks for the next start condition.

```
# find start, end point pairs; return df with added values
final_kpi_paired_df = add_event_delta_paired(
    df=df_sorted,
    col_prefix='correspondence',
    id_field=id_field,
    date_field=event_date_field,
    start_conditions={'event_type': 'Correspondence', 'is_employee': False},
    end_conditions={'event_type': 'Correspondence', 'is_employee': True},
    start_flag='start',
    end_flag='end'
)
```

### Additional helper functions

#### chronumbo.core.sql.create_engine()

A one-stop shop for creating a SQLAlchemy engine for MSSQL, postgreSQL, or MySQL.

Many users will have their own constructions of this, or will simply use the basic SQLAlchemy functions to do this, but this is a helpful tool for doing the connection formatting work for you.

```
# create SQLAlchemy connection engine
engine = create_engine(
    db=db,                          # name of database
    dialect=dialect,                # 'postgres', 'mysql', or 'mssql'
    user=user,
    password=password,
    endpoint=endpoint,
    verbose=True                    # if True, prints status to terminal; for dev and debug
)
```

#### chronumbo.core.sql.db_to_df()

While many users will have their own construction of this, this is a variant on `pd.read_sql()` with built-in error handling. Given a SQLAlchemy engine and a SQL query, returns the query as a DataFrame.

```
query = """
    SELECT * FROM project_audit_trail
"""

df = db_to_df(
    query=query,
    engine=engine,
    verbose=True
)
```

#### chronumbo.core.sql.df_to_db()

Unlike the simplicity of `db_to_df()`, this function utilises `df.to_sql()` to push a DataFrame to SQL, with the optional functionality of handling dtypes between DataFrames and SQL to ensure successful upload.

```
df_to_db(
    engine=engine,
    df=df,
    tbl='event_log_with_time',      # name of SQL table to upload data to
    if_tbl_exists='replace',        # as with df.to_sql()
    retrieve_dtype_from_db=True,    # if True, recasts DataFrame with SQL field types
    dtype_override=None,            # dictionary of column names and dtypes
    chunksize=10000,
    verbose=True
)
```

#### chronumbo.core.sql.get_sql_col_types()

Helper function to retrieve column types from SQL tables.

🚨 _See [Issue #5](https://github.com/heynicejacket/chronumbo/issues/5); This function currently only supports postgreSQL._

```
get_sql_col_types(
    engine=engine,
    tbl=tbl,
    verbose=True
)
```

#### chronumbo.core.toolkit.the_time_keeper()

the_time_keeper() isn't specifically used in this project; time delta calculations are handled directly in `add_event_delta_single()` and `add_event_delta_pairs()`. I include it within this project as many event logs can be millions of rows long, and during dev and debug, this can be helpful to gauge how long your operations take.

Example usage is as follows:

```
start_time = the_time_keeper()      # init with no value passed to t; time script begins
# do stuff
the_time_keeper(start_time)         # pass value to t; print duration of task
```
