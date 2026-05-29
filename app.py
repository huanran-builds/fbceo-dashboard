import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd
from data import get_all_data, get_aqi_category, get_aqi_color

FONTS = ["https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;600;700&display=swap"]

app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=FONTS)
server = app.server

df = get_all_data(days=180)

G = "#2d7a1f"
DARK = "#111"
MID = "#555"
RED = "#c0392b"
FONT = "Open Sans, sans-serif"

def build_time_chart(days):
    filtered = df.tail(days)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=filtered["date"],
        y=filtered["pm25"],
        mode="lines",
        line=dict(color=G, width=2),
        fill="tozeroy",
        fillcolor="rgba(45,122,31,0.08)",
    ))
    fig.add_hline(
        y=35, line_dash="dash", line_color=RED, line_width=1,
        annotation_text="EPA limit 35 µg/m³",
        annotation_position="top left",
        annotation_font_size=11,
        annotation_font_color=RED
    )
    fig.update_layout(
        margin=dict(l=40, r=20, t=20, b=40),
        showlegend=False,
        plot_bgcolor="white",
        paper_bgcolor="white",
        yaxis_title="PM2.5 µg/m³",
        font=dict(family=FONT, size=12, color=DARK),
        yaxis=dict(gridcolor="#efefef", zeroline=False),
        xaxis=dict(gridcolor="#efefef", zeroline=False)
    )
    return fig

def build_worst_days():
    worst = df.nlargest(10, "pm25").sort_values("pm25", ascending=True)
    colors = [get_aqi_color(v) for v in worst["pm25"]]
    fig = go.Figure(go.Bar(
        x=worst["pm25"],
        y=worst["date"].dt.strftime("%b %d, %Y"),
        orientation="h",
        marker_color=colors,
        marker_line_width=0,
        text=worst["pm25"].apply(lambda x: f"{x} µg/m³"),
        textposition="outside",
        textfont=dict(size=11, family=FONT)
    ))
    fig.update_layout(
        margin=dict(l=80, r=80, t=10, b=30),
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis_title="PM2.5 µg/m³",
        font=dict(family=FONT, size=12, color=DARK),
        showlegend=False,
        xaxis=dict(gridcolor="#efefef", zeroline=False)
    )
    return fig

def build_donut():
    df["category"] = df["pm25"].apply(get_aqi_category)
    counts = df["category"].value_counts()
    color_map = {
        "Good": "#2d7a1f",
        "Moderate": "#e6b800",
        "Unhealthy for Sensitive Groups": "#D85A30",
        "Unhealthy": "#A32D2D",
        "Very Unhealthy": "#791F1F"
    }
    fig = go.Figure(go.Pie(
        labels=counts.index,
        values=counts.values,
        hole=0.6,
        marker_colors=[color_map.get(c, "#888") for c in counts.index],
        textinfo="label+percent",
        textfont=dict(size=11, family=FONT),
        insidetextorientation="radial"
    ))
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="white",
        showlegend=False,
        font=dict(family=FONT, size=12)
    )
    return fig

latest_pm25 = df["pm25"].iloc[-1] if not df.empty else 0
current_category = get_aqi_category(latest_pm25)
current_color = get_aqi_color(latest_pm25)
avg_30d = round(df.tail(30)["pm25"].mean(), 1) if not df.empty else 0
unhealthy_days = len(df[df["pm25"] > 35.4])
peak_pm25 = df["pm25"].max() if not df.empty else 0

def card(label, value, sub, accent=DARK):
    return html.Div([
        html.P(label, style={"fontSize": "11px", "color": MID, "margin": "0 0 8px", "letterSpacing": "0.5px", "fontFamily": FONT}),
        html.P(value, style={"fontSize": "32px", "fontWeight": "700", "margin": "0", "color": accent, "lineHeight": "1", "fontFamily": FONT}),
        html.P(sub, style={"fontSize": "12px", "color": MID, "margin": "6px 0 0", "fontFamily": FONT})
    ], style={
        "padding": "20px 24px",
        "borderBottom": f"3px solid {accent}",
        "background": "white",
        "borderRadius": "4px",
        "border": "1px solid #e8e8e8",
        "borderBottom": f"3px solid {accent}",
    })

app.layout = html.Div([

    html.Div([
        html.Div([
            html.Img(
                src="https://fbh-environmental.com/wp-content/uploads/2022/09/county_dark_100.png",
                style={"height": "40px"}
            ),
            html.Span("Fort Bend Houston Environmental", style={
                "fontSize": "14px", "fontWeight": "600", "color": "white",
                "fontFamily": FONT, "marginLeft": "12px"
            }),
        ], style={"display": "flex", "alignItems": "center"}),
        html.A("Report a smell →",
               href="https://docs.google.com/forms/d/1f9MKiy-x8xHcsI_kadRFnCta00mF4DTkFlBgBWkduEk/viewform",
               target="_blank",
               style={"fontSize": "13px", "color": "white", "fontFamily": FONT,
                      "border": "1px solid rgba(255,255,255,0.4)", "padding": "6px 16px",
                      "borderRadius": "4px", "textDecoration": "none"})
    ], style={
        "background": "#1a3a0f",
        "padding": "12px 32px",
        "display": "flex",
        "justifyContent": "space-between",
        "alignItems": "center"
    }),

    html.Div([

        html.Div([
            html.Div([
                html.P("Missouri City · Super Neighborhood 41", style={
                    "fontSize": "13px", "color": MID, "margin": "0 0 4px", "fontFamily": FONT
                }),
                html.H1("Air Quality Dashboard", style={
                    "fontSize": "28px", "fontWeight": "700", "margin": "0",
                    "color": DARK, "fontFamily": FONT
                }),
                html.P("Live data from 4 PurpleAir community sensors", style={
                    "fontSize": "13px", "color": MID, "margin": "6px 0 0", "fontFamily": FONT
                })
            ]),
            html.Div([
                html.P("Current reading", style={
                    "fontSize": "12px", "color": MID, "margin": "0 0 4px",
                    "textAlign": "right", "fontFamily": FONT
                }),
                html.P(f"{latest_pm25} µg/m³", style={
                    "fontSize": "36px", "fontWeight": "700", "margin": "0",
                    "color": current_color, "textAlign": "right", "fontFamily": FONT, "lineHeight": "1"
                }),
                html.P(current_category, style={
                    "fontSize": "13px", "color": current_color, "margin": "6px 0 0",
                    "textAlign": "right", "fontFamily": FONT, "fontWeight": "600"
                })
            ])
        ], style={
            "display": "flex", "justifyContent": "space-between", "alignItems": "flex-start",
            "padding": "32px 0 24px", "borderBottom": "1px solid #e8e8e8", "marginBottom": "24px"
        }),

        html.Div([
            card("30-day avg PM2.5", f"{avg_30d}", "µg/m³ daily average", G),
            card("Unhealthy days", str(unhealthy_days), "past 6 months", RED),
            card("Active sensors", "4", "community monitors", DARK),
            card("Peak PM2.5", str(peak_pm25), "µg/m³ recorded", RED),
        ], style={
            "display": "grid", "gridTemplateColumns": "repeat(4, 1fr)",
            "gap": "12px", "marginBottom": "32px"
        }),

        html.Div([
            html.Div([
                html.P("About this neighborhood", style={
                    "fontSize": "11px", "fontWeight": "600", "color": MID,
                    "margin": "0 0 6px", "letterSpacing": "0.5px", "fontFamily": FONT,
                    "textTransform": "uppercase"
                }),
                html.P([
                    "Super Neighborhood 41 is a majority Black and Hispanic community in southwest Houston surrounded by landfills, active oil wells, and chemical plants. The nearest official EPA monitor is ",
                    html.Strong("7 miles away", style={"color": DARK}),
                    ". These sensors exist because residents demanded to know what they're breathing."
                ], style={"fontSize": "14px", "color": MID, "margin": "0", "lineHeight": "1.7", "fontFamily": FONT})
            ], style={"flex": "2", "paddingRight": "40px", "borderRight": "1px solid #e8e8e8"}),

            html.Div([
                html.P("6,600+", style={"fontSize": "28px", "fontWeight": "700", "margin": "0", "color": DARK, "fontFamily": FONT}),
                html.P("resident complaints filed", style={"fontSize": "12px", "color": MID, "margin": "2px 0 0", "fontFamily": FONT})
            ], style={"flex": "1", "padding": "0 32px", "borderRight": "1px solid #e8e8e8"}),

            html.Div([
                html.P("222", style={"fontSize": "28px", "fontWeight": "700", "margin": "0", "color": RED, "fontFamily": FONT}),
                html.P("investigations out of 6,600", style={"fontSize": "12px", "color": MID, "margin": "2px 0 0", "fontFamily": FONT})
            ], style={"flex": "1", "padding": "0 32px", "borderRight": "1px solid #e8e8e8"}),

            html.Div([
                html.P("150K+ lbs", style={"fontSize": "28px", "fontWeight": "700", "margin": "0", "color": RED, "fontFamily": FONT}),
                html.P("toxics emitted since 2009", style={"fontSize": "12px", "color": MID, "margin": "2px 0 0", "fontFamily": FONT})
            ], style={"flex": "1", "paddingLeft": "32px"})

        ], style={
            "display": "flex", "alignItems": "center",
            "padding": "24px 28px", "background": "#f9f9f7",
            "borderRadius": "4px", "border": "1px solid #e8e8e8", "marginBottom": "32px"
        }),

        html.Div([
            html.Div([
                html.H2("PM2.5 over time", style={"fontSize": "16px", "fontWeight": "600", "margin": "0", "color": DARK, "fontFamily": FONT}),
                html.P("Daily average across all sensors", style={"fontSize": "12px", "color": MID, "margin": "3px 0 0", "fontFamily": FONT})
            ]),
            dcc.Dropdown(
                id="range-dropdown",
                options=[
                    {"label": "30 days", "value": 30},
                    {"label": "90 days", "value": 90},
                    {"label": "180 days", "value": 180}
                ],
                value=30,
                clearable=False,
                style={"width": "130px", "fontSize": "13px", "fontFamily": FONT}
            )
        ], style={"display": "flex", "justifyContent": "space-between", "alignItems": "flex-start", "marginBottom": "8px"}),

        dcc.Graph(id="time-chart", figure=build_time_chart(30), style={"height": "240px"}),

        html.P("Days above the red dashed EPA standard (35 µg/m³) pose elevated health risks — especially for children, elderly residents, and those with asthma or heart conditions.",
               style={"fontSize": "12px", "color": "#999", "margin": "8px 0 32px", "fontFamily": FONT}),

        html.Div([
            html.Div([
                html.H2("Worst air quality days", style={"fontSize": "16px", "fontWeight": "600", "margin": "0 0 4px", "color": DARK, "fontFamily": FONT}),
                html.P("Highest recorded PM2.5 — past 6 months", style={"fontSize": "12px", "color": MID, "margin": "0 0 8px", "fontFamily": FONT}),
                dcc.Graph(figure=build_worst_days(), style={"height": "280px"})
            ], style={"flex": "1", "paddingRight": "32px", "borderRight": "1px solid #e8e8e8"}),

            html.Div([
                html.H2("Days by AQI category", style={"fontSize": "16px", "fontWeight": "600", "margin": "0 0 4px", "color": DARK, "fontFamily": FONT}),
                html.P("How often was the air safe to breathe?", style={"fontSize": "12px", "color": MID, "margin": "0 0 8px", "fontFamily": FONT}),
                dcc.Graph(figure=build_donut(), style={"height": "240px"}),
            ], style={"flex": "1", "paddingLeft": "32px"})
        ], style={"display": "flex", "marginBottom": "32px"}),

        html.Div([
            html.Div([
                html.Div([
                    html.P("Smell something in your neighborhood?", style={
                        "fontSize": "15px", "fontWeight": "600", "color": DARK,
                        "margin": "0 0 4px", "fontFamily": FONT
                    }),
                    html.P("Help FBCEO track pollution events by reporting bad odors. Takes less than a minute.",
                           style={"fontSize": "13px", "color": MID, "margin": "0", "fontFamily": FONT})
                ]),
                html.A("Report a bad smell →",
                       href="https://docs.google.com/forms/d/1f9MKiy-x8xHcsI_kadRFnCta00mF4DTkFlBgBWkduEk/viewform",
                       target="_blank",
                       style={
                           "fontSize": "13px", "color": "white", "background": G,
                           "padding": "10px 20px", "borderRadius": "4px",
                           "textDecoration": "none", "fontFamily": FONT,
                           "fontWeight": "600", "whiteSpace": "nowrap"
                       })
            ], style={
                "display": "flex", "justifyContent": "space-between", "alignItems": "center",
                "padding": "20px 24px", "background": "#f9f9f7",
                "border": "1px solid #e8e8e8", "borderRadius": "4px", "marginBottom": "24px"
            }),

            html.P([
                "Data sourced from ",
                html.A("PurpleAir", href="https://map.purpleair.com", target="_blank",
                       style={"color": G, "textDecoration": "none", "fontFamily": FONT}),
                " community sensors · ",
                html.A("fbh-environmental.com", href="https://fbh-environmental.com", target="_blank",
                       style={"color": G, "textDecoration": "none", "fontFamily": FONT}),
                " · Sensors: Settlers Park and 3 nearby monitors in Missouri City"
            ], style={"fontSize": "12px", "color": "#aaa", "margin": "0", "fontFamily": FONT})
        ], style={"borderTop": "1px solid #e8e8e8", "paddingTop": "20px", "paddingBottom": "32px"})

    ], style={"maxWidth": "1000px", "margin": "0 auto", "padding": "0 32px"}),

], style={"background": "white", "minHeight": "100vh"})

@app.callback(
    Output("time-chart", "figure"),
    Input("range-dropdown", "value")
)
def update_time_chart(days):
    return build_time_chart(days)

if __name__ == "__main__":
    app.run(debug=True)