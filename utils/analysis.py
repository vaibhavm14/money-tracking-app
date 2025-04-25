import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import pandas as pd
import os
from database import get_transactions # Assumes database.py is in the root
from datetime import datetime # Needed for timestamp

# Ensure matplotlib uses a non-interactive backend suitable for saving files
import matplotlib
matplotlib.use('Agg')

PLOT_FILENAME = "assets/analysis_plot.png"

def generate_analysis_plot():
    """Generates and saves the income vs expense pie chart."""
    transactions = get_transactions()
    if not transactions:
        print("No transactions found for analysis.")
        return None, None # No data

    try:
        df = pd.DataFrame(transactions, columns=['id', 'amount', 'description', 'currency', 'type', 'date'])
        df['amount'] = pd.to_numeric(df['amount'])
        df['date'] = pd.to_datetime(df['date'])
    except Exception as e:
        print(f"Error processing transactions into DataFrame: {e}")
        return None, None

    credits = df[df['type'] == 'credit']['amount'].sum()
    debits = df[df['type'] == 'debit']['amount'].sum()

    # Basic Stats
    total_transactions = len(df)
    avg_credit = df[df['type'] == 'credit']['amount'].mean() if credits > 0 else 0
    avg_debit = df[df['type'] == 'debit']['amount'].mean() if debits > 0 else 0
    balance = credits - debits

    stats = {
        "Total Transactions": total_transactions,
        "Total Income": f"{credits:.2f}",
        "Total Expenses": f"{debits:.2f}",
        "Current Balance": f"{balance:.2f}",
        "Average Income Transaction": f"{avg_credit:.2f}",
        "Average Expense Transaction": f"{avg_debit:.2f}",
    }

    # --- Plot Generation ---
    plt.style.use('seaborn-v0_8-darkgrid') # Use a nice style
    fig, ax = plt.subplots(figsize=(5, 5)) # Smaller figure

    labels = ['Income', 'Expenses']
    values = [credits, debits]
    colors = ['#4CAF50', '#F44336'] # Green, Red

    # Only plot if there are values
    if credits > 0 or debits > 0:
         wedges, texts, autotexts = ax.pie(
             values, labels=labels, autopct='%1.1f%%', startangle=140,
             colors=colors, textprops={'color':"w", 'weight':'bold'}, # White text on wedges
             wedgeprops={'edgecolor': 'black'} # Add edge color
         )
         # Improve autopct text color for visibility
         for autotext in autotexts:
             autotext.set_color('white')
    else:
         ax.text(0.5, 0.5, "No data to display", ha='center', va='center', fontsize=12, color='black')


    ax.set_title('Income vs Expenses', color='black', weight='bold') # Title color
    fig.patch.set_facecolor('white') # White background for the figure itself

    # Save in current directory for simplicity
    plot_path = PLOT_FILENAME

    try:
        os.makedirs(os.path.dirname(plot_path), exist_ok=True)
        plt.savefig(plot_path, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight', pad_inches=0.1)
        print(f"Analysis plot saved to {plot_path}")
    except Exception as e:
        print(f"Error saving plot: {e}")
        plot_path = None # Indicate failure
    finally:
         plt.close(fig) # Close the figure to free memory

    return plot_path, stats