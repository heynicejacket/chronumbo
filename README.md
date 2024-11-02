![chronumbo](https://github.com/heynicejacket/chronodetective/blob/master/chronumbo-banner.png)

Because there's always just one more thing being asked by a client.

# chronumbo

## Why?

## Some basic terminology

While some terminology is fairly universal, many terms are infinitely varied across different industries, companies, and corporate cultures. For the purposes of this project, we'll define here a few placeholder terms.

* **Project** - these sorts of asks can be for projects, services, orders, bugs, etc.; for simplicity's sake, I will refer to these generically as "projects". While the particulars of these differ widely, the collection of data is broadly the same.
* **Current State Table** - a table which generally has one row per project, with the latest data for that project (e.g. current status, current assignee, etc.).
* **Event Log Table** - a table which has one row per event, and many rows per project.
* **Project ID** - the unique identifier for the Current State Table.
* **Event ID** - the unique identifier for rows in the Event Log Table.

### Example datasets

In the test files (`chronumbo.test`) you can see 

## Basic Implentation

The most basic implementation is simply calling either `add_event_delta_single()` with the following general logic:

* `df` a DataFrame containing Event Log Table, ordered by ID and date
* `id_field` the Project ID

or `add_event_delta_pairs()`, with

* 

You can feed a DataFrame into either on your own, but for the less tech-savvy (and the lazy), I've included in this project the following functions to get you going with minimal work:

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

# sort by IDs and date
df_sorted = df.sort_values(by=[id_field, event_date_field])
```

### add_event_delta_single()
<center>![chronumbo single pair](https://github.com/heynicejacket/chronodetective/blob/master/chronumbo-single-pair.png)</center>

```
# find start, end point pair; return df with added values
final_kpi_single_df = add_event_delta_single(
    df=df_sorted,
    col_prefix='project_res_time',
    id_field=id_field,
    date_field=event_date_field,
    start_conditions={'event_type': 'Status', 'event_description': 'Created'},
    end_conditions={'event_type': 'Status', 'event_description': 'Resolved'},
    start_flag='start',
    end_flag='end',
    end_at_latest=False,
    use_earliest_if_no_start=True,
    use_latest_if_no_end=True
)
```

### add_event_delta_pairs()
<center>![chronumbo multi pair](https://github.com/heynicejacket/chronodetective/blob/master/chronumbo-multi-pair.png)</center>

```
# find start, end point pairs; return df with added values
final_kpi_paired_df = add_event_delta_paired(
    df=df_sorted,
    col_prefix='correspondence',
    id_field=id_field,
    date_field=event_date_field,
    start_conditions={'event_type': 'Correspondence', 'is_employee': True},
    end_conditions={'event_type': 'Correspondence', 'is_employee': False},
    start_flag='start',
    end_flag='end'
)
```

### Additional helper functions
