import pandas as pd
import pygsheets
import config

from flask import Flask, jsonify, render_template

app = Flask(__name__)

@app.route("/")
def index():
    """Return the homepage."""
    return render_template("index.html")

@app.route("/lineup")
def lineUp():
    # Access google sheet with data
    gc = pygsheets.authorize(service_file=config.google_api_file_path)
    sh = gc.open_by_key(config.sheet_key)
    worksheets = sh.worksheets()

    # Specify most current sheet
    no_sheets = len(worksheets)
    index_value = no_sheets - 1
    current_stats = sh[index_value]

    # Import sheet as dataframe 
    stats_df = current_stats.get_as_df(has_header=True, index_column=None)

    # Create dataframe with running backs only and sort for greatest to least by Points
    running_backs = stats_df.loc[stats_df["Category"] == "RB"]
    running_backs.sort_values(by="Proj Points", ascending=False, inplace=True)
    running_backs = running_backs.reset_index(drop=True)


    lineup_rb = pd.DataFrame(columns=stats_df.columns)
    lineup_wr = pd.DataFrame(columns=stats_df.columns)

    # Set tier level to select players
    index_level = 0

    # Select first running back (RB1)
    cond = running_backs.iloc[index_level]
    lineup_rb = lineup_rb.append(cond, ignore_index=True)


    # Create dataframe with wide receivers only and sort for greatest to least by Points
    wide_receiver = stats_df.loc[stats_df["Category"] == "WR"]
    wide_receiver.sort_values(by="Proj Points", ascending=False, inplace=True)
    wide_receiver = wide_receiver.reset_index(drop=True)


    # Select first receiver (WR1)
    cond = wide_receiver.iloc[index_level]
    lineup_wr = lineup_wr.append(cond, ignore_index=True)
    index_level += 2

    # Assign points of players to variables being compared 
    RB_points = running_backs.loc[index_level, "Proj Points"]
    WR_points = wide_receiver.loc[index_level, "Proj Points"]

    # Add RB or WR depending on point values
    if RB_points > WR_points:
        cond = running_backs.iloc[index_level]
        lineup_rb = lineup_rb.append(cond, ignore_index=True)
        index_level += 2
    else:
        cond = wide_receiver.iloc[index_level]
        lineup_wr = lineup_wr.append(cond, ignore_index=True)
        index_level += 2

    # Determine count of RB and WR in lineup
    rb_count = lineup_rb["Name"].count()

    wr_count = lineup_wr["Name"].count()

    # Compare and add players based on number of players already on roster
    if rb_count < 2 and wr_count < 3:
        if RB_points > WR_points:
            cond = running_backs.iloc[index_level]
            lineup_rb = lineup_rb.append(cond, ignore_index=True)
            index_level += 3
            rb_count = lineup_rb["Name"].count()
            print(rb_count)
        else:
            cond = wide_receiver.iloc[index_level]
            lineup_wr = lineup_wr.append(cond, ignore_index=True)
            index_level += 3
            wr_count = lineup_wr["Name"].count()
            print(wr_count)
    else:
        print("...")


    if rb_count < 2 and wr_count < 3:
        if RB_points > WR_points:
            cond = running_backs.iloc[index_level]
            lineup_rb = lineup_rb.append(cond, ignore_index=True)
            index_level += 4
            rb_count = lineup_rb["Name"].count()

        else:
            cond = wide_receiver.iloc[index_level]
            lineup_wr = lineup_wr.append(cond, ignore_index=True)
            index_level += 4
            wr_count = lineup_wr["Name"].count()

    elif rb_count == 2:
        cond = wide_receiver.iloc[index_level]
        lineup_wr = lineup_wr.append(cond, ignore_index=True)
        index_level += 4
        wr_count = lineup_wr["Name"].count()

    elif wr_count == 3:
        cond = running_backs.iloc[index_level]
        lineup_rb = lineup_rb.append(cond, ignore_index=True)
        index_level += 4
        rb_count = lineup_rb["Name"].count()

    else:
        print("...")



    while wr_count < 3:
        try:
            cond = wide_receiver.iloc[index_level]
            lineup_wr = lineup_wr.append(cond, ignore_index=True)
            index_level += 4
            wr_count = lineup_wr["Name"].count()

        except:
            print(lineup_wr["Name"].count())


    # Join RB and WR lineups into one dataframe
    lineup = pd.concat([lineup_rb, lineup_wr], ignore_index=True)
    lineup = lineup.reset_index(drop=True)
    lineup


    # Salary checkpoint
    salary = lineup["Salary($K)"].sum()
    remaining_salary = 50 - salary
    remaining_salary


    # Create dataframe with flex players only and sort for greatest to least by Points
    flex = stats_df.loc[stats_df["Category"] == "FLEX"]
    flex.sort_values(by="Proj Points", ascending=False, inplace=True)
    flex = flex.reset_index(drop=True)


    # Create tuples to compare flex players and players already in lineup.  Only add players from flex list who are not already in the line up.  Once the lineup has a total of 6 players, do not add any additional players.
    lineupTuples = [
        (item.Name, item.Position, item.Team) for index, item in lineup.iterrows()
    ]

    flex2 = flex.iloc[index_level:]

    lineup_count = lineup["Name"].count()

    for index, item in flex2.iterrows():
        var_o = item.Name, item.Position, item.Team
        if var_o not in lineupTuples and lineup_count < 6:
            cond = flex.iloc[index]
            lineup = lineup.append(cond, ignore_index=True)
            lineup_count = lineup["Name"].count()
        else:
            break


    quarter_back = stats_df.loc[stats_df["Category"] == "QB"]
    quarter_back.sort_values(by="Proj Points", ascending=False, inplace=True)
    quarter_back = quarter_back.reset_index(drop=True)


    tight_end = stats_df.loc[stats_df["Category"] == "TE"]
    tight_end.sort_values(by="Proj Points", ascending=False, inplace=True)
    tight_end = tight_end.reset_index(drop=True)


    QB_points = quarter_back.loc[index_level, "Proj Points"]
    TE_points = tight_end.loc[index_level, "Proj Points"]

    if QB_points > TE_points:
        cond = quarter_back.iloc[index_level]
        lineup = lineup.append(cond, ignore_index=True)
        index_level += 5

        cond = tight_end.iloc[index_level]
        lineup = lineup.append(cond, ignore_index=True)
        index_level += 5

    else:
        cond = tight_end.iloc[index_level]
        lineup = lineup.append(cond, ignore_index=True)
        index_level += 5

        cond = quarter_back.iloc[index_level]
        lineup = lineup.append(cond, ignore_index=True)
        index_level += 5



    defense = stats_df.loc[stats_df["Category"] == "DST"]
    defense.sort_values(by="Proj Points", ascending=False, inplace=True)
    defense = defense.reset_index(drop=True)
    defense.head(5)



    cond = defense.iloc[index_level]
    lineup = lineup.append(cond, ignore_index=True)

    print(lineup)

    salary = lineup["Salary($K)"].sum()
    remaining_salary = 50 - salary
    print(remaining_salary)

    lineup_list=[]

    for index, item in lineup.iterrows():
        lineupDict={}
        lineupDict['a_Name']=item[0]
        lineupDict['b_Position']=item[1]
        lineupDict['c_Category']=item[2]
        lineupDict['d_Team']=item[3]
        lineupDict['e_Salary']=item[4]
        lineupDict['f_Points']=item[5]
        lineupDict['g_Pt/$/K']=item[6]
        
        lineup_list.append(lineupDict)

    return jsonify(lineup_list)

if __name__ == "__main__":
    app.run()