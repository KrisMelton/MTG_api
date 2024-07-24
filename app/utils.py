import pandas as pd
import requests
import os
import logging
from typing import List, Tuple, Optional
import plotly.express as px
import plotly.io as pio

from config import API_URL, CSV_DIRECTORY, OUTPUT_EXCEL_FILE, COLUMNS_TO_DROP

def fetch_bulk_data_info(url: str) -> Optional[dict]:
    """Fetches the bulk data information from the Scryfall API."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Error fetching bulk data info: {e}")
        return None

def get_oracle_cards_url(bulk_data_info: dict) -> Optional[str]:
    """Extracts the URL for the Oracle Cards JSON file."""
    return next((item['download_uri'] for item in bulk_data_info['data'] if item['type'] == 'oracle_cards'), None)

def download_oracle_cards_data(url: str) -> Optional[List[dict]]:
    """Downloads the Oracle Cards JSON data."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Error downloading Oracle Cards data: {e}")
        return None

def clean_data(data: List[dict], columns_to_drop: List[str]) -> pd.DataFrame:
    """Cleans the Oracle Cards data by dropping unnecessary columns and extracting the USD price."""
    df = pd.DataFrame(data)
    df_cleaned = df.drop(columns=[col for col in columns_to_drop if col in df.columns], errors='ignore')
    if 'prices' in df.columns:
        df_cleaned['usd'] = df['prices'].apply(lambda x: x.get('usd') if isinstance(x, dict) else None)
    else:
        df_cleaned['usd'] = None  # Set default value if 'prices' column is missing
    logging.info("Columns in cleaned DataFrame: %s", df_cleaned.columns)
    return df_cleaned

def collect_merged_data(df_cleaned: pd.DataFrame, csv_directory: str) -> List[Tuple[str, pd.DataFrame]]:
    """Collects the merged data for each CSV file."""
    csv_files = [os.path.join(csv_directory, f) for f in os.listdir(csv_directory) if f.endswith('.csv')]
    merged_data = []
    
    for csv_file in csv_files:
        deck_df = pd.read_csv(csv_file)
        required_columns = ['name', 'usd']
        if all(col in df_cleaned.columns for col in required_columns):
            merged_df = pd.merge(deck_df[['name']], df_cleaned[required_columns], on='name', how='inner')
            merged_df['usd'] = pd.to_numeric(merged_df['usd'], errors='coerce')
            total_usd = merged_df['usd'].sum()
            merged_df['total'] = total_usd
            sheet_name = os.path.basename(csv_file).split('.')[0]
            merged_data.append((sheet_name, total_usd, merged_df))
        else:
            logging.warning(f"Skipping merge for {csv_file}: Required columns missing in df_cleaned.")
    
    return merged_data

def write_to_excel(merged_data: List[Tuple[str, pd.DataFrame]], output_file: str) -> None:
    """Writes the collected merged data to an Excel file."""
    if not merged_data:
        logging.warning("No valid sheets to write to the Excel file. Please check your data and try again.")
        return
    
    with pd.ExcelWriter(output_file) as writer:
        for sheet_name, total_usd, merged_df in merged_data:
            merged_df.to_excel(writer, sheet_name=sheet_name, index=False)

def process_data() -> Tuple[str, List[Tuple[str, float]]]:
    bulk_data_info = fetch_bulk_data_info(API_URL)
    if bulk_data_info is None:
        return "Error fetching bulk data info.", []
    
    oracle_cards_url = get_oracle_cards_url(bulk_data_info)
    if oracle_cards_url is None:
        logging.error("Oracle Cards URL not found.")
        return "Oracle Cards URL not found.", []
    
    oracle_cards_data = download_oracle_cards_data(oracle_cards_url)
    if oracle_cards_data is None:
        return "Error downloading Oracle Cards data.", []
    
    df_cleaned = clean_data(oracle_cards_data, COLUMNS_TO_DROP)
    merged_data = collect_merged_data(df_cleaned, CSV_DIRECTORY)
    write_to_excel(merged_data, OUTPUT_EXCEL_FILE)
    logging.info("Data processing complete. Output saved to: %s", OUTPUT_EXCEL_FILE)
    deck_values = [(sheet_name, total_usd) for sheet_name, total_usd, _ in merged_data]
    return "Data processing complete.", deck_values

def generate_graph(deck_values: List[Tuple[str, float]]) -> str:
    df = pd.DataFrame(deck_values, columns=['Deck', 'Value'])
    fig = px.bar(df, x='Deck', y='Value', title='Deck Values')
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    return pio.to_html(fig, full_html=False, div_id='plotly-graph')
