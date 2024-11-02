![chronumbo](https://github.com/heynicejacket/chronodetective/blob/master/chronumbo-banner.png)

Because there's always just one more thing being asked by a client.

# chronumbo

## Why?

### Example datasets

## Basic Implentation

```
engine = create_engine(                                         # create SQL connection engine
    db=db,
    dialect=dialect,
    user=user,
    password=password,
    endpoint=endpoint,
    verbose=verbose
)

df = db_to_df(                                                  # create DataFrame from SQL query
    query=audit_query,
    engine=engine,
    verbose=verbose
)

df_sorted = df.sort_values(by=[id_field, event_date_field])     # sort by IDs and date
```

### add_event_delta_single()
![chronumbo single pair](https://github.com/heynicejacket/chronodetective/blob/master/chronumbo-single-pair.png)

```
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
```

### add_event_delta_pairs()
![chronumbo multi pair](https://github.com/heynicejacket/chronodetective/blob/master/chronumbo-multi-pair.png)

```
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
```
