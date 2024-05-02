# Currency conversion rates (as of a certain date)
GBP_to_USD_rate = 1.36
GBP_to_EUR_rate = 1.17
USD_to_EUR_rate = 0.86

# Function to convert initial amount based on currency
def convert_to_currency(amount, currency):
    if currency == 'GBP':
        return amount
    elif currency == 'USD':
        return amount / GBP_to_USD_rate
    elif currency == 'EUR':
        return amount / GBP_to_EUR_rate

# Example usage
initial_amount = 1000  # Initial amount in GBP
selected_currency = 'EUR'  # User selected currency
initial_amount_in_selected_currency = convert_to_currency(initial_amount, selected_currency)

print(f"Initial amount in {selected_currency}: {initial_amount_in_selected_currency}")
