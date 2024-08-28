import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

class EnergyConsumptionAnalyzer:
    def __init__(self, csv_file):
        #Initialize the class with the path to the CSV file
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        self.read()

    def read(self):
        # Read the CSV file and set up the SQLite database
        data = pd.read_csv('owid-energy-data.csv')
        data.to_sql('energy_consumption_data', self.conn, if_exists='replace', index=False)

    def get_country_data(self, country):
        #Retrieve data for the specified country from the database.
        query = """
        SELECT *
        FROM energy_consumption_data
        WHERE LOWER(country) = ?
        ORDER BY year
        """
        return pd.read_sql_query(query, self.conn, params=(country.lower(),))

    def analyze_trends(self, data):
        # Filter data to include only records from 1980 to 2022
        data = data[(data['year'] >= 1980) & (data['year'] <= 2023)]

        # Calculate the total consumption of fossil fuels
        fossil_fuels = ['coal_consumption', 'oil_consumption', 'gas_consumption']
        if all(fuel in data.columns for fuel in fossil_fuels):
            data['fossil_fuel_consumption'] = data[fossil_fuels].sum(axis=1)
        else:
            data['fossil_fuel_consumption'] = 0  

        # Calculate the total consumption of renewable energy sources
        renewable_energy = ['biofuel_consumption', 'hydro_consumption', 'solar_consumption', 'wind_consumption']
        if all(source in data.columns for source in renewable_energy):
            data['renewable_consumption'] = data[renewable_energy].sum(axis=1)
        else:
            data['renewable_consumption'] = 0 

        return data

    def plot_trends(self, data, country):
        # Plot trends in fossil fuel and renewable energy consumption.
        plt.figure(figsize=(15, 8))
        plt.plot(data['year'], data['fossil_fuel_consumption'], label='Fossil Fuel Consumption (TWh)', marker='o', color='r')
        plt.plot(data['year'], data['renewable_consumption'], label='Renewable Consumption (TWh)', marker='o', color='g')
        plt.title(f'Renewable vs. Non-Renewable Energy Consumption in {country}')
        plt.xlabel('Year')
        plt.ylabel('Energy Consumption (TWh)')
        plt.legend()
        plt.grid(True)
        plt.show()

    def run_comparison(self):
        # Prompt the user to enter a country they want to analyze, restarts if no data is available
        while True:
            country = input("Enter Country for Energy Consumption Comparison: ")
            country_data = self.get_country_data(country)
        
            if country_data.empty:
                print(f"No data available for {country}. Please try another country.")
            else:
                analyzed_data = self.analyze_trends(country_data)
                self.plot_trends(analyzed_data, country)
                break

    def close(self):
        self.conn.close()

# Usage 
if __name__ == "__main__":
    energyComparison = EnergyConsumptionAnalyzer('owid-energy-data.csv')
    energyComparison.run_comparison()
    energyComparison.close()
