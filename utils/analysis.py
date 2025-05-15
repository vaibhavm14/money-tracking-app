import matplotlib
matplotlib.use('Agg') # Use non-interactive backend before importing pyplot
import matplotlib.pyplot as plt
import pandas as pd
import os
from database import get_transactions

# Ensure assets directory exists for the plot
PLOT_DIR = "assets"
PLOT_FILENAME = os.path.join(PLOT_DIR, "analysis_plot.png")

# --- Define Exchange Rates ---
# Base currency is INR. All amounts will be converted to INR for analysis.
# These are approximate rates. For a real app, fetch these dynamically.
EXCHANGE_RATES_TO_INR = {
    "INR": 1.0,
    "USD": 83.0, # 1 USD = 83 INR (approx)
    "EUR": 90.0, # 1 EUR = 90 INR (approx)
    "GBP": 105.0, # 1 GBP = 105 INR (approx)
    "JPY": 0.55, # 1 JPY = 0.55 INR (approx)
    # Add other currencies as needed
}
BASE_CURRENCY_ANALYSIS = "INR"

def convert_to_base_currency(amount, currency):
    """Converts an amount from a given currency to the base currency (INR)."""
    rate = EXCHANGE_RATES_TO_INR.get(currency.upper(), None)
    if rate is None:
        print(f"Warning: Exchange rate for {currency} not found. Using 1.0 (no conversion).")
        return amount # Or handle as an error, or skip the transaction
    return amount * rate

def generate_analysis_plot():
    """
    Generates an income vs expense pie chart and calculates financial statistics,
    converting all amounts to a base currency (INR).
    """
    transactions = get_transactions()
    if not transactions:
        print("No transactions found for analysis.")
        return None, None

    try:
        # Columns from DB: id, amount, description, currency, transaction_type, date, tag
        # Ensure the columns list matches the data structure from get_transactions()
        df = pd.DataFrame(transactions, columns=['id', 'original_amount', 'description', 'currency', 'type', 'date', 'tag'])
        df['original_amount'] = pd.to_numeric(df['original_amount'])

        # Convert amounts to base currency (INR)
        df['amount_in_base_currency'] = df.apply(
            lambda row: convert_to_base_currency(row['original_amount'], row['currency']),
            axis=1
        )
    except Exception as e:
        print(f"Error processing transactions into DataFrame or converting currency: {e}")
        return None, None

    # Calculations are now done on 'amount_in_base_currency'
    credits_in_base = df[df['type'] == 'credit']['amount_in_base_currency'].sum()
    debits_in_base = df[df['type'] == 'debit']['amount_in_base_currency'].sum()

    # Basic Stats
    total_transactions = len(df)
    num_credits = len(df[df['type'] == 'credit'])
    num_debits = len(df[df['type'] == 'debit'])
    
    avg_credit_in_base = df[df['type'] == 'credit']['amount_in_base_currency'].mean() if num_credits > 0 else 0
    avg_debit_in_base = df[df['type'] == 'debit']['amount_in_base_currency'].mean() if num_debits > 0 else 0
    balance_in_base = credits_in_base - debits_in_base

    stats = {
        "Total Transactions": total_transactions,
        "Total Income": f"{credits_in_base:.2f}", # Values are now in base currency
        "Total Expenses": f"{debits_in_base:.2f}",
        "Current Balance": f"{balance_in_base:.2f}",
        "Average Income Transaction": f"{avg_credit_in_base:.2f}",
        "Average Expense Transaction": f"{avg_debit_in_base:.2f}",
        # "Base Currency": BASE_CURRENCY_ANALYSIS # Optional: to display which currency is used
    }

    # --- Plot Generation (uses converted amounts) ---
    try:
        plt.style.use('seaborn-v0_8-darkgrid')
        fig, ax = plt.subplots(figsize=(5, 5))

        labels = ['Income', 'Expenses']
        # Use the converted values for the plot
        values = [credits_in_base, debits_in_base]
        colors = ['#4CAF50', '#F44336']

        if credits_in_base > 0 or debits_in_base > 0:
            wedges, texts, autotexts = ax.pie(
                values, autopct='%1.1f%%', startangle=140,
                colors=colors, textprops={'color': "w", 'weight': 'bold'},
                wedgeprops={'edgecolor': 'black'}
            )
            ax.legend(wedges, labels, title="Categories (in INR)", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
            plt.setp(autotexts, size=10, weight="bold", color="white")
        else:
            ax.text(0.5, 0.5, "No data to display", ha='center', va='center', fontsize=12, color='black')

        ax.set_title(f'Income vs Expenses (in {BASE_CURRENCY_ANALYSIS})', color='black', weight='bold')
        fig.patch.set_facecolor('white')

        os.makedirs(os.path.dirname(PLOT_FILENAME), exist_ok=True)
        
        plt.savefig(PLOT_FILENAME, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight', pad_inches=0.1)
        plot_path = PLOT_FILENAME
        print(f"Analysis plot saved to {plot_path}")
    except Exception as e:
        print(f"Error generating or saving plot: {e}")
        plot_path = None
    finally:
        if 'fig' in locals():
            plt.close(fig)

    return plot_path, stats