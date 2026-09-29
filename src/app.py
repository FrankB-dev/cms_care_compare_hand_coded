from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import sqlite3
import pandas as pd

# Get Measure Descriptions for the filter
conn = sqlite3.connect("../data/care_compare.db")
query = "SELECT DISTINCT [Measure Description] " \
        "FROM complications_and_deaths_national"

measures = pd.read_sql_query(query, conn)
measures = sorted(measures['Measure Description'].tolist())
conn.close()

app = Dash()

app.layout = [
    html.H1(children='National Complications and Deaths Explorer', style={'textAlign':'center'}),
    dcc.Dropdown(measures, measures[0], id='dropdown-selection'),
    dcc.Graph(id='graph-content')
]

@callback(
    Output('graph-content', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_graph(value):
    conn = sqlite3.connect("../data/care_compare.db")
    cursor = conn.cursor()
    query = """
        SELECT 
            [National Rate],
            [End Date YMD],
            [Unit of Measure]
        FROM
            complications_and_deaths_national
        WHERE
            [Measure Description] = ?
        ORDER BY [End Date YMD]
    """ 
    cursor.execute(query, (value,))
    results = cursor.fetchall()
    df = pd.DataFrame(
        columns=['National Rate', 'End Date Str', 'Unit of Measure'],
        data=results
    )
    df['End Date'] = pd.to_datetime(df['End Date Str'])
    uom = df['Unit of Measure'].unique()[0]
    return px.line(df, x='End Date', y='National Rate', 
                   labels={"National Rate": f"National Rate, {uom}"},
                   markers=True)

if __name__ == '__main__':
    app.run(debug=True, threaded=False)