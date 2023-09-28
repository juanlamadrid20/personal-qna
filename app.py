import dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from utils import load_chain  # Loading your custom function
from flask import Flask

company_logo = 'https://www.app.nl/wp-content/uploads/2019/01/Blendle.png'
chain = load_chain()
messages = [{"role": "assistant", "content": "Hi human! I am your smart AI. How can I help you today?"}]

server = Flask(__name__)
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP], server=server)

app.layout = dbc.Container(
    fluid=True,
    children=[
        dbc.Row(dbc.Col(dbc.Card(dbc.CardBody("Your Notion Chatbot"), color="primary"))),
        dbc.Row(dbc.Col(dbc.Card(
            dbc.CardBody(
                [dbc.ListGroupItem(message["content"], color="light", className=message["role"]) for message in messages],
                id='messages',
            ),
            color="secondary"
        ))),
        dbc.Row(
            [
                dbc.Col(dbc.Input(value='', type='text', id='query')),
                dbc.Col(dbc.Button('Submit', id='submit-button', color="primary", className="mr-1")),
            ],
            className="my-3",
        ),
    ],
)


@app.callback(
    Output('messages', 'children'),
    Input('submit-button', 'n_clicks'),
    State('query', 'value'),
    prevent_initial_call=True
)
def update_chat(n_clicks, value):
    global messages
    # Add user message to chat history
    messages.append({"role": "user", "content": value})
    # Send user's question to our chain
    result = chain({"question": value})
    response = result['answer']
    # Add assistant message to chat history
    messages.append({"role": "assistant", "content": response})

    return [dbc.ListGroupItem(message["content"], color="light", className=message["role"]) for message in messages]


if __name__ == '__main__':
    app.run_server(debug=True)