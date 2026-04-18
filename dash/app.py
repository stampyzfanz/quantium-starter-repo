from pathlib import Path

import dash
import pandas as pd
import plotly.express as px
from dash import ctx
from dash import Input, Output
from dash import dcc, html


def load_sales_data() -> pd.DataFrame:
    data_path = Path(__file__).resolve().parent.parent / "data" / "pink_morsel_sales.csv"

    df = pd.read_csv(data_path)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["sales"] = pd.to_numeric(df["sales"], errors="coerce")
    df["region"] = df["region"].astype(str).str.strip().str.lower()
    df = df.dropna(subset=["date", "sales"])

    return df


def build_figure(df: pd.DataFrame, selected_region: str):
    if selected_region == "all":
        filtered = df
        title_suffix = "All Regions"
    else:
        filtered = df[df["region"] == selected_region]
        title_suffix = selected_region.capitalize()

    daily_sales = filtered.groupby("date", as_index=False).agg(sales=("sales", "sum"))

    fig = px.line(
        daily_sales,
        x="date",
        y="sales",
        title=f"Pink Morsel Sales Over Time ({title_suffix})",
    )
    fig.update_layout(
        title={"x": 0.5, "xanchor": "center"},
        xaxis_title="Date",
        yaxis_title="Sales ($)",
        template="plotly_dark",
        paper_bgcolor="#0f172a",
        plot_bgcolor="#111827",
        font={"family": "sans-serif", "color": "#e5e7eb"},
    )
    cutoff_date = "2021-01-15"
    fig.add_shape(
        type="line",
        x0=cutoff_date,
        x1=cutoff_date,
        y0=0,
        y1=1,
        yref="paper",
        line={"dash": "dash", "color": "#f59e0b"},
    )
    fig.add_annotation(
        x=cutoff_date,
        y=1,
        yref="paper",
        text="Price increase date",
        showarrow=False,
        xanchor="left",
        yanchor="bottom",
        font={"color": "#f59e0b"},
    )
    return fig


def region_button_styles(selected_region: str) -> tuple[dict, dict, dict, dict, dict]:
    base = {
        "fontFamily": "sans-serif",
        "padding": "8px 14px",
        "borderRadius": "8px",
        "border": "1px solid #374151",
        "backgroundColor": "#1f2937",
        "color": "#e5e7eb",
        "cursor": "pointer",
    }
    active = {
        **base,
        "backgroundColor": "#2563eb",
        "border": "1px solid #3b82f6",
        "fontWeight": "600",
    }

    return (
        active if selected_region == "north" else base,
        active if selected_region == "east" else base,
        active if selected_region == "south" else base,
        active if selected_region == "west" else base,
        active if selected_region == "all" else base,
    )


def create_layout() -> html.Div:
    sales_data = load_sales_data()

    if sales_data.empty:
        return html.Div(
            [
                html.H1("Pink Morsel Sales Timeline"),
                html.P("No valid sales data was found in data/pink_morsel_sales.csv."),
            ],
            style={
                "maxWidth": "1000px",
                "margin": "0 auto",
                "padding": "24px",
                "fontFamily": "sans-serif",
                "color": "#e5e7eb",
                "backgroundColor": "#0b1220",
                "minHeight": "100vh",
            },
        )

    north_style, east_style, south_style, west_style, all_style = region_button_styles("all")

    return html.Div(
        [
            html.H1("Pink Morsel Sales Timeline"),
            html.P("Daily total Pink Morsel sales from the provided dataset."),
            dcc.Store(id="selected-region", data="all"),
            html.Div(
                [
                    html.Button("North", id="region-north", n_clicks=0, style=north_style),
                    html.Button("East", id="region-east", n_clicks=0, style=east_style),
                    html.Button("South", id="region-south", n_clicks=0, style=south_style),
                    html.Button("West", id="region-west", n_clicks=0, style=west_style),
                    html.Button("All", id="region-all", n_clicks=0, style=all_style),
                ],
                style={"display": "flex", "gap": "8px", "flexWrap": "wrap", "marginBottom": "12px"},
            ),
            dcc.Graph(id="sales-chart", figure=build_figure(sales_data, "all")),
        ],
        style={
            "maxWidth": "1000px",
            "margin": "0 auto",
            "padding": "24px",
            "fontFamily": "sans-serif",
            "color": "#e5e7eb",
            "backgroundColor": "#0b1220",
            "minHeight": "100vh",
        },
    )


app = dash.Dash(__name__)
app.title = "Pink Morsel Sales Dashboard"
app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            html, body {
                margin: 0;
                padding: 0;
                background-color: #0b1220;
                font-family: sans-serif;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""
app.layout = create_layout()


@app.callback(
    Output("selected-region", "data"),
    Input("region-north", "n_clicks"),
    Input("region-east", "n_clicks"),
    Input("region-south", "n_clicks"),
    Input("region-west", "n_clicks"),
    Input("region-all", "n_clicks"),
)
def set_selected_region(_north: int, _east: int, _south: int, _west: int, _all: int):
    button_to_region = {
        "region-north": "north",
        "region-east": "east",
        "region-south": "south",
        "region-west": "west",
        "region-all": "all",
    }
    triggered_id = ctx.triggered_id if isinstance(ctx.triggered_id, str) else "region-all"
    return button_to_region.get(triggered_id, "all")


@app.callback(
    Output("sales-chart", "figure"),
    Output("region-north", "style"),
    Output("region-east", "style"),
    Output("region-south", "style"),
    Output("region-west", "style"),
    Output("region-all", "style"),
    Input("selected-region", "data"),
)
def update_chart(selected_region: str):
    sales_data = load_sales_data()
    button_styles = region_button_styles(selected_region)
    return (build_figure(sales_data, selected_region), *button_styles)


if __name__ == "__main__":
    app.run(debug=True)
