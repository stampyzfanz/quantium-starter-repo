from pathlib import Path

import dash
import pandas as pd
import plotly.express as px
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
        xaxis_title="Date",
        yaxis_title="Sales ($)",
        template="plotly_white",
    )
    cutoff_date = "2021-01-15"
    fig.add_shape(
        type="line",
        x0=cutoff_date,
        x1=cutoff_date,
        y0=0,
        y1=1,
        yref="paper",
        line={"dash": "dash", "color": "crimson"},
    )
    fig.add_annotation(
        x=cutoff_date,
        y=1,
        yref="paper",
        text="Price increase date",
        showarrow=False,
        xanchor="left",
        yanchor="bottom",
        font={"color": "crimson"},
    )
    return fig


def create_layout() -> html.Div:
    sales_data = load_sales_data()

    if sales_data.empty:
        return html.Div(
            [
                html.H1("Pink Morsel Sales Timeline"),
                html.P("No valid sales data was found in data/pink_morsel_sales.csv."),
            ],
            style={"maxWidth": "1000px", "margin": "0 auto", "padding": "24px"},
        )

    return html.Div(
        [
            html.H1("Pink Morsel Sales Timeline"),
            html.P("Daily total Pink Morsel sales from the provided dataset."),
            dcc.RadioItems(
                id="region-filter",
                options=[
                    {"label": "North", "value": "north"},
                    {"label": "East", "value": "east"},
                    {"label": "South", "value": "south"},
                    {"label": "West", "value": "west"},
                    {"label": "All", "value": "all"},
                ],
                value="all",
                inline=True,
                style={"marginBottom": "12px"},
            ),
            dcc.Graph(id="sales-chart", figure=build_figure(sales_data, "all")),
        ],
        style={"maxWidth": "1000px", "margin": "0 auto", "padding": "24px"},
    )


app = dash.Dash(__name__)
app.title = "Pink Morsel Sales Dashboard"
app.layout = create_layout()


@app.callback(Output("sales-chart", "figure"), Input("region-filter", "value"))
def update_chart(selected_region: str):
    sales_data = load_sales_data()
    return build_figure(sales_data, selected_region)


if __name__ == "__main__":
    app.run(debug=True)
