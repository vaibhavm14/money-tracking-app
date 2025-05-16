from kivy_garden.graph import Graph, MeshLinePlot, BarPlot
from kivy.metrics import dp
from kivy.graphics.texture import Texture
from kivy.core.image import Image as CoreImage
from kivy.clock import Clock
from database import get_transactions
import os
import io

# Ensure assets directory exists for the plot
PLOT_DIR = "assets"
PLOT_FILENAME = os.path.join(PLOT_DIR, "analysis_plot.png")

# --- Define Exchange Rates ---
# Base currency is INR. All amounts will be converted to INR for analysis.
EXCHANGE_RATES_TO_INR = {
    "INR": 1.0,
    "USD": 83.0,  # 1 USD = 83 INR (approx)
    "EUR": 90.0,  # 1 EUR = 90 INR (approx)
    "GBP": 105.0,  # 1 GBP = 105 INR (approx)
    "JPY": 0.55,  # 1 JPY = 0.55 INR (approx)
}
BASE_CURRENCY_ANALYSIS = "INR"

def convert_to_base_currency(amount, currency):
    """Converts an amount from a given currency to the base currency (INR)."""
    rate = EXCHANGE_RATES_TO_INR.get(currency.upper(), None)
    if rate is None:
        print(f"Warning: Exchange rate for {currency} not found. Using 1.0 (no conversion).")
        return amount
    return amount * rate

def generate_analysis_plot():
    """
    Generates income vs expense bar graph and calculates financial statistics,
    converting all amounts to a base currency (INR).
    """
    transactions = get_transactions()
    if not transactions:
        print("No transactions found for analysis.")
        return None, None, None

    # Process transaction data
    credits_in_base = 0
    debits_in_base = 0
    credit_transactions = []
    debit_transactions = []

    for transaction in transactions:
        # Unpack transaction tuple
        _, amount, _, currency, t_type, date, tag = transaction
        amount_in_base = convert_to_base_currency(float(amount), currency)
        
        if t_type == 'credit':
            credits_in_base += amount_in_base
            credit_transactions.append(transaction)
        elif t_type == 'debit':
            debits_in_base += amount_in_base
            debit_transactions.append(transaction)

    # Basic Stats
    total_transactions = len(transactions)
    num_credits = len(credit_transactions)
    num_debits = len(debit_transactions)
    
    avg_credit_in_base = credits_in_base / num_credits if num_credits > 0 else 0
    avg_debit_in_base = debits_in_base / num_debits if num_debits > 0 else 0
    balance_in_base = credits_in_base - debits_in_base

    stats = {
        "Total Transactions": total_transactions,
        "Total Income": f"{credits_in_base:.2f}",
        "Total Expenses": f"{debits_in_base:.2f}",
        "Current Balance": f"{balance_in_base:.2f}",
        "Average Income Transaction": f"{avg_credit_in_base:.2f}",
        "Average Expense Transaction": f"{avg_debit_in_base:.2f}",
    }

    # Create and save visualization
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(PLOT_FILENAME), exist_ok=True)
        
        # Generate chart data for analysis screen
        chart_data = {
            'categories': ['Income', 'Expenses'],
            'values': [credits_in_base, debits_in_base],
            'colors': [(0.3, 0.8, 0.3, 1), (0.8, 0.3, 0.3, 1)]  # Green for income, Red for expenses
        }
        
        return PLOT_FILENAME, stats, chart_data
        
    except Exception as e:
        print(f"Error generating analysis data: {e}")
        return None, None, None