import dash
from flask import Flask, render_template, jsonify, request,redirect
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly 
import plotly.graph_objs as go
import json
import yfinance as yf
from dotenv import load_dotenv
import datetime, os
import plotly.graph_objs as go
from plotly_dash import plotly_dash_function


app = Flask(__name__)

dash_app = Dash(__name__, server=app, url_base_pathname='/dash/')


dash_app.layout = html.Div([
        html.H1("Real Time Stock data"),
        
        html.Div([
            dcc.Dropdown(
                id= 'stock-name-id',
                options= [
                    {'label': 'TCS', 'value':'TCS.NS'},
                    {'label': 'Apple', 'value':'AAPL'},
                    {'label': 'Bitcoin', 'value':'BTC-USD'},
                    {'label': 'Facebook', 'value':'META'},
                    {'label': 'Maruti Suzuki India Limited', 'value':'MARUTI.NS'},
                    {'label': 'Cipla Limited', 'value':'CIPLA.NS'},
                    {'label': 'Wipro Limited', 'value':'WIPRO.NS'},
                    {'label': 'Google', 'value':'GOOGL'},
                    {'label': 'Bajaj Finance Limited', 'value':'BAJFINANCE.NS'},
                    {'label': 'Tata Steel Limited', 'value':'TATASTEEL.NS'},

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
          html.Button('Normal Plotly', id='home-button', n_clicks=0),
          dcc.Location(id='url', refresh=True) , 
        dcc.Graph(id = 'final-graph'),
       
    ])

@dash_app.callback(
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


@app.route("/", methods = ['GET', 'POST'])
def get_data():
    if request.method == 'POST':
        frontend_data = request.get_json()
        stock_name = frontend_data.get('stock')   
        graph_name = frontend_data.get('graph')
        period = frontend_data.get('period')
        # print(stock_name)
        # print(graph_name)
        # print(period)
        load_dotenv()
        ticker_name = os.getenv(f'{stock_name.upper()}')
        
        interval = None
        if(period == '1d'):
            interval = '1m'
        elif(period == '1w'):
            period = '5d'
            interval = '5m'         
        elif(period == '1m'):
            period = '1mo' 
            interval = '15m'        
        elif(period == '1y'):
            interval = '5d'
                        
        elif(period == '5y'):
            interval = '1mo'  
                    
        
        data = yf.download(tickers= str(ticker_name), period=f'{period}', interval= f'{interval}')
        # print(data)
        if not data.empty:
            if graph_name == 'candlestick':
                fig = go.Figure(data=[go.Candlestick(x=data.index,
                                                     open=data['Open'],
                                                     high=data['High'],
                                                     low=data['Low'],
                                                     close=data['Close'])])
            elif graph_name == 'line':
                fig = go.Figure(data=go.Scatter(x=data.index, y=data['Close'], mode='lines'))
            elif graph_name == 'bar':
                fig = go.Figure(data=go.Bar(x=data.index, y=data['Close']))
            elif graph_name == 'area':
                fig = go.Figure(data=go.Scatter(x=data.index, y=data['Close'], fill='tozeroy'))

            graph_html = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        return jsonify(graph_html=graph_html)
        
        
    return render_template('index.html')


@app.route('/dash')
def dash():
    return redirect('/dash/')


@dash_app.callback(
    Output('url', 'pathname'),
    Input('home-button', 'n_clicks')
)
def go_home(n_clicks):
    if n_clicks > 0:
        return '/'
    return dash.no_update


if __name__ == '__main__':
    app.run(debug=True,)