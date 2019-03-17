def build_report_table(extra_queries):
    table = []

    column_names = ["Serializer", "Field", "Function", "Max queries"]
    rows = [query.to_row() for query in extra_queries]
    max_width = max(len(item) for row in rows for item in row)

    table.append(
        " | ".join(column_name.ljust(max_width) for column_name in column_names)
    )

    # Separator
    table.append("-+-".join(["-" * max_width] * len(column_names)))

    for row in rows[1:]:
        table.append(" | ".join(column.ljust(max_width) for column in row))

    return table
