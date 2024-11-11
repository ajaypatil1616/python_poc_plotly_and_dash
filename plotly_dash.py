from dash import Dash, dcc, html
from dash.dependencies import Input, Output
from datetime import datetime, timedelta

import plotly.graph_objs as go
import yfinance as yf

def plotly_dash_function():
 

    app = Dash(__name__)

    app.layout = html.Div([
        html.H1("Real Time Stock data"),
        
        html.Div([
            dcc.Dropdown(
                id= 'stock-name-id',
                options= [
                    {'label': 'TCS', 'value':'TCS.NS'},
                    {'label': 'Apple', 'value':'AAPL'},
                    {'label': 'Bitcoin', 'value':'BTC-USD'},
                    {'label': 'Facebook', 'value':'META'},
                ],
                value= 'TCS.NS', 
                clearable= False
            )
        ]),
        
        html.Div([
            dcc.Dropdown(
                id= 'graph-name-id',
                options = [
                    {'label': 'Line', 'value':'line'},
                    {'label': 'Candlestick', 'value':'candlestick'},
                ],
                value= 'line',
                clearable= False
            )
        ]),
        html.Div([
            dcc.Dropdown(
                id='period-id',
                options=[
                    {'label':'1 Day', 'value': '1d'},
                    {'label':'1 Week', 'value': '5d'},
                    {'label':'1 Month', 'value': '1mo'},
                    {'label':'1 Year', 'value': '1y'},
                    {'label':'5 Year', 'value': '5y'},
                ], 
                value= '1d',
                clearable= False
            )
        ]),
        dcc.Interval(id = 'refresh-id', interval= 1* 1000, n_intervals=0),
        dcc.Graph(id = 'final-graph')
    ])

    @app.callback(
        Output('final-graph', 'figure'),
        Input('period-id', 'value'),
        Input('graph-name-id', 'value'),
        Input('stock-name-id', 'value'),
        Input('refresh-id', 'n_intervals'),
    )
    def update_graph(period, graph_name, stock_name, n_intervals):
            if(period == '1d'):
                interval = '1m'
            elif(period == '5d'):            
                interval = '5m'         
            elif(period == '1mo'):            
                interval = '15m'        
            elif(period == '1y'):
                interval = '5d'                        
            elif(period == '5y'):
                interval = '1mo' 
            data = yf.download(tickers=f'{stock_name}',period=f'{period}', interval= f'{interval}')
            # print(data)
            
            if not data.empty:
                if graph_name == 'line':
                    figure = go.Figure(data = [go.Scatter(x = data.index, y= data['Close'], mode='lines',)])
                elif graph_name == 'candlestick' :
                    figure = go.Figure(data = [go.Candlestick(x=data.index , 
                                                            open= data['Open'],
                                                            high = data['High'],
                                                            low = data['Low'],
                                                            close = data['Close'],
                                                            )])
                figure.update_layout(title = f"{stock_name} over Time")
                return figure

    if __name__ == '__main__':
        app.run_server(debug = True)