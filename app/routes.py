from flask import Blueprint, render_template, send_file
from .utils import process_data, generate_graph
from config import OUTPUT_EXCEL_FILE

main = Blueprint('main', __name__)

@main.route('/')
def index():
    status, deck_values = process_data()
    formatted_deck_values = [(deck, f"${value:,.2f}") for deck, value in deck_values]
    graph = generate_graph(deck_values)
    return render_template('index.html', status=status, deck_values=formatted_deck_values, graph=graph)

@main.route('/download')
def download_file():
    return send_file(OUTPUT_EXCEL_FILE, as_attachment=True)
