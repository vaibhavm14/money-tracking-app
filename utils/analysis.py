import matplotlib
matplotlib.use('Agg') # Use non-interactive backend before importing pyplot
import matplotlib.pyplot as plt
import pandas as pd
import os
from database import get_transactions # Assumes database.py is in the root/project directory
# from datetime import datetime # Not strictly needed here anymore

# Ensure assets directory exists for the plot
PLOT_DIR = "assets"
PLOT_FILENAME = os.path.join(PLOT_DIR, "analysis_plot.png")

def generate_analysis_plot():
    """
    Generates an income vs expense pie chart and calculates financial statistics.

    Returns:
        tuple: (plot_path, stats_dict)
               plot_path (str): Path to the saved plot image, or None if failed.
               stats_dict (dict): Dictionary of statistics, or None if no data or error.
    """
    transactions = get_transactions()
    if not transactions:
        print("No transactions found for analysis.")
        return None, None # No data to process

    try:
        df = pd.DataFrame(transactions, columns=['id', 'amount', 'description', 'currency', 'type', 'date'])
        df['amount'] = pd.to_numeric(df['amount'])
        # df['date'] = pd.to_datetime(df['date']) # Date conversion not strictly needed for this analysis
    except Exception as e:
        print(f"Error processing transactions into DataFrame: {e}")
        return None, None

    credits = df[df['type'] == 'credit']['amount'].sum()
    debits = df[df['type'] == 'debit']['amount'].sum()

    # Basic Stats
    total_transactions = len(df)
    num_credits = len(df[df['type'] == 'credit'])
    num_debits = len(df[df['type'] == 'debit'])
    
    avg_credit = df[df['type'] == 'credit']['amount'].mean() if num_credits > 0 else 0
    avg_debit = df[df['type'] == 'debit']['amount'].mean() if num_debits > 0 else 0
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
    try:
        plt.style.use('seaborn-v0_8-darkgrid')
        fig, ax = plt.subplots(figsize=(5, 5)) # Keep figure size manageable

        labels = ['Income', 'Expenses']
        values = [credits, debits]
        colors = ['#4CAF50', '#F44336'] # Green for income, Red for expenses

        if credits > 0 or debits > 0:
            wedges, texts, autotexts = ax.pie(
                values, autopct='%1.1f%%', startangle=140,
                colors=colors, textprops={'color': "w", 'weight': 'bold'},
                wedgeprops={'edgecolor': 'black'}
            )
            # Set labels outside or ensure autotext is clearly visible
            ax.legend(wedges, labels, title="Categories", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
            plt.setp(autotexts, size=10, weight="bold", color="white")
        else:
            ax.text(0.5, 0.5, "No data to display", ha='center', va='center', fontsize=12, color='black')

        ax.set_title('Income vs Expenses', color='black', weight='bold')
        fig.patch.set_facecolor('white') # Figure background

        # Ensure assets directory exists
        os.makedirs(os.path.dirname(PLOT_FILENAME), exist_ok=True)
        
        plt.savefig(PLOT_FILENAME, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight', pad_inches=0.1)
        plot_path = PLOT_FILENAME
        print(f"Analysis plot saved to {plot_path}")
    except Exception as e:
        print(f"Error generating or saving plot: {e}")
        plot_path = None # Indicate failure
    finally:
        if 'fig' in locals(): # Ensure fig exists before trying to close
            plt.close(fig) # Close the figure to free memory

    # If plot generation failed but stats were calculated, still return stats.
    # However, if the core data processing failed, stats would also be None.
    return plot_path, stats