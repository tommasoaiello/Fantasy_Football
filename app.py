from flask import Flask, request, jsonify, render_template
import pandas as pd

app = Flask(__name__)

# Load the CSV file (adjust path to your CSV file)
csv_file = 'stats_with_links.csv'
df_stats = pd.read_csv(csv_file)

def get_player_stats(player_name):
    player_data = df_stats[df_stats['Nome'] == player_name]
    
    if player_data.empty:
        return None
    
    player_stats = {}

    # Recap details (Nome, Squadra, R, Rm, FVM, FVM_M)
    recap = player_data[['Nome', 'Squadra', 'R', 'Rm', 'FVM', 'FVM_M']].iloc[0].to_dict()

    # Columns in the desired order
    columns_order = ['Pv', 'Mv', 'Fm', 'Gf', 'Ass', 'Squadra', 'Rc', 'R+', 'R-', 'Amm', 'Esp', 'Au', 'Gs', 'Rp']

    # Helper function to rename season-specific columns and add the link
    def strip_season_suffix(df, year, link_column):
        df = df.copy()  # Create a copy of the DataFrame
        # Rename columns by removing the season suffix
        rename_dict = {f'{col}_{year}': col for col in columns_order if f'{col}_{year}' in df.columns}
        df.rename(columns=rename_dict, inplace=True)
        # Add the link to the DataFrame if the link column exists
        if link_column in player_data.columns:
            df['link'] = player_data[link_column].values[0]
        return df[columns_order + ['link']] if 'link' in df.columns else df[columns_order]

    # Filter columns for the current season
    available_columns = [col for col in columns_order if col in player_data.columns]
    current_stats = player_data[available_columns].dropna(axis=1)
    
    # Add the link for the current season from 'Link_2024_25'
    if not current_stats.empty:
        current_stats_dict = current_stats[columns_order].to_dict(orient='records')[0]
        if 'Link_2024_25' in player_data.columns:
            current_stats_dict['link'] = player_data['Link_2024_25'].values[0]
        player_stats['current'] = current_stats_dict

    # Add stats for past seasons (2024/25, 2023/24, 2022/23, 2021/22)
    for year, link_col in zip(['2024_25', '2023_24', '2022_23', '2021_22'], 
                              ['Link_2024_25', 'Link_2023_24', 'Link_2022_23', 'Link_2021_22']):
        season_columns = [f'{col}_{year}' for col in columns_order]
        available_columns = [col for col in season_columns if col in player_data.columns]
        
        season_stats = player_data[available_columns].dropna(axis=1)
        if not season_stats.empty:
            # Strip the season suffix and add the link to the stats
            stripped_season_stats = strip_season_suffix(season_stats, year, link_col)
            player_stats[year] = stripped_season_stats.to_dict(orient='records')[0]
    
    return {'recap': recap, 'stats': player_stats} if player_stats else None

# Route to serve the index.html file
@app.route('/')
def index():
    return render_template('index.html')

# API endpoint to handle player search
@app.route('/search_player', methods=['GET'])
def search_player():
    player_name = request.args.get('player_name')
    
    if not player_name:
        return jsonify({'error': 'Player name is required'}), 400
    
    # Retrieve player stats
    data = get_player_stats(player_name)

    # print(data)
    
    if data:
        return jsonify({'player': player_name, 'recap': data['recap'], 'stats': data['stats']}), 200
    else:
        return jsonify({'error': 'Player not found or no valid stats available'}), 404

# New endpoint to handle player suggestions
@app.route('/player_suggestions', methods=['GET'])
def player_suggestions():
    query = request.args.get('query', '')
    # Filter players whose names contain the query (case-insensitive)
    suggestions = df_stats[df_stats['Nome'].str.contains(query, case=False, na=False)]['Nome'].unique().tolist()
    
    return jsonify(suggestions)

if __name__ == '__main__':
    app.run(debug=True)