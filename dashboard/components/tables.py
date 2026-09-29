import dash_ag_grid as dag

from utils.formatting import humanize_column


def customer_grid(df, id_col, page_size=12):
    columns = []
    for col in df.columns:
        col_def = {
            "field": col,
            "headerName": humanize_column(col),
            "sortable": True,
            "filter": "agTextColumnFilter",
            "resizable": True,
        }
        if col == id_col:
            col_def["pinned"] = "left"
        if str(df[col].dtype).startswith(("int", "float")):
            col_def["filter"] = "agNumberColumnFilter"
        columns.append(col_def)
    return dag.AgGrid(
        id="cluster-customer-grid",
        rowData=df.to_dict("records"),
        columnDefs=columns,
        defaultColDef={"minWidth": 130},
        dashGridOptions={"pagination": True, "paginationPageSize": page_size, "rowSelection": "single", "animateRows": True},
        className="ag-theme-quartz-dark bankiq-grid",
    )
