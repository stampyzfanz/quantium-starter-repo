from pathlib import Path

import dash
import pandas as pd
import plotly.express as px
from dash import dcc, html


def load_daily_sales() -> pd.DataFrame:
    data_path = Path(__file__).resolve().parent.parent / "data" / "pink_morsel_sales.csv"

    df = pd.read_csv(data_path)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["sales"] = pd.to_numeric(df["sales"], errors="coerce")
    df = df.dropna(subset=["date", "sales"])

    if df.empty:
        return pd.DataFrame(columns=["date", "sales"])

    daily_sales = df.groupby("date", as_index=False).agg(sales=("sales", "sum"))

    return daily_sales


def build_figure(daily_sales: pd.DataFrame):
    fig = px.line(
        daily_sales,
        x="date",
        y="sales",
        title="Pink Morsel Sales Over Time",
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
    daily_sales = load_daily_sales()

    if daily_sales.empty:
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
            dcc.Graph(figure=build_figure(daily_sales)),
        ],
        style={"maxWidth": "1000px", "margin": "0 auto", "padding": "24px"},
    )


app = dash.Dash(__name__)
app.title = "Pink Morsel Sales Dashboard"
app.layout = create_layout()


if __name__ == "__main__":
    app.run(debug=True)
