import pandas as pd

def load_stats_file() -> pd.DataFrame:
    # File paths
    file_2021_22 = 'stats/Stagione_2021_22.xlsx'
    file_2022_23 = 'stats/Stagione_2022_23.xlsx'
    file_2023_24 = 'stats/Stagione_2023_24.xlsx'
    file_2024_25 = 'stats/Stagione_2024_25.xlsx'

    quotas = 'stats/listone_2024_25.xlsx'
    

    df_quotas = pd.read_excel(quotas)

    # Load the Excel files into DataFrames
    df_2021_22 = pd.read_excel(file_2021_22)
    df_2022_23 = pd.read_excel(file_2022_23)
    df_2023_24 = pd.read_excel(file_2023_24)
    df_2024_25 = pd.read_excel(file_2024_25)



    # Ensure consistent player column across all dataframes
    player_column = 'Id'  # Adjust this if the column name is different
    
    # Initialize a new DataFrame with only players from df_2024_25
    df_combined = df_2024_25.copy()

    df_combined = pd.merge(df_combined, df_quotas, on=player_column, how='left')

    # Merge statistics from df_2023_24
    df_combined = pd.merge(df_combined, df_2023_24, on=player_column, how='left', suffixes=('', '_2023_24'))

    # Merge statistics from df_2022_23
    df_combined = pd.merge(df_combined, df_2022_23, on=player_column, how='left', suffixes=('', '_2022_23'))

    # Merge statistics from df_2021_22
    df_combined = pd.merge(df_combined, df_2021_22, on=player_column, how='left', suffixes=('', '_2021_22'))

    df_combined = df_combined[df_combined.columns.drop(list(df_combined.filter(regex='Nome_')))]

    df_combined = df_combined[df_combined.columns.drop(list(df_combined.filter(regex='R_')))]

    df_combined = df_combined[df_combined.columns.drop(list(df_combined.filter(regex='Rm_')))]

    return df_combined

# Call the function and store the result in a variable 'stats'
stats = load_stats_file()

# Optional: Preview the first few rows of the combined stats
stats.to_csv('Total_stats.csv', index=False)