DTYPE_MAPPING = {
    # integer types
    'integer': 'int64',
    'bigint': 'int64',
    'smallint': 'int64',
    'tinyint': 'int8',
    'mediumint': 'int32',

    # unsigned integer types, treated as signed in pandas
    'unsigned big int': 'uint64',
    'unsigned int': 'uint32',
    'unsigned smallint': 'uint16',
    'unsigned tinyint': 'uint8',

    # floating-point types
    'decimal': 'float64',
    'numeric': 'float64',
    'real': 'float64',
    'float': 'float64',
    'double precision': 'float64',

    # date and time types
    'date': 'datetime64[ns]',
    'datetime': 'datetime64[ns]',
    'timestamp': 'datetime64[ns]',
    'time': 'datetime64[ns]',                               # pandas lacks time-only dtype; can be stored as datetime
    'year': 'datetime64[ns]',                               # pandas lacks year dtype; can be stored as datetime

    # char types
    'char': 'object',
    'varchar': 'object',
    'text': 'object',
    'mediumtext': 'object',
    'longtext': 'object',
    'tinytext': 'object',

    # binary data types
    'binary': 'object',                                     # pandas lacks binary natively; can be stored as object
    'varbinary': 'object',
    'blob': 'object',
    'mediumblob': 'object',
    'longblob': 'object',
    'tinyblob': 'object',

    # boolean types
    'boolean': 'bool',
    'bool': 'bool',

    # JSON data types
    'json': 'object',
    'jsonb': 'object',                                      # postgreSQL JSON binary

    # geospatial types
    'geometry': 'object',
    'geography': 'object',
    'point': 'object',
    'linestring': 'object',
    'polygon': 'object',

    # enumerated types
    'enum': 'object',

    # UUID types
    'uuid': 'object',

    # array types
    'array': 'object',

    # interval types
    'interval': 'timedelta64[ns]',

    # specialized types
    'money': 'float64',                                     # money can be treated as float or custom object
    'serial': 'int64',                                      # auto-incrementing integer
    'bigserial': 'int64',

    # bit types
    'bit': 'object',
    'bit varying': 'object',
}
