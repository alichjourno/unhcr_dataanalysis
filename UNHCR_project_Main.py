############### DATA INFOS ###################
### Refugee data is from the UNHCR API &   ###
### Population data is from the world bank ###
##############################################

##### Load packages #####

import requests
import pandas as pd
import pypopulation
import dash
from dash import html
from dash import dcc
import plotly.express as px
from dash.dependencies import Input, Output

##### API #####

# Request to API for global data on refugees in country of asylum

url_global = "https://api.unhcr.org/population/v1/population/?page=&limit=1000&yearFrom=&yearTo=&year=2022&download=&coo=&coa=&coo_all=&coa_all=true&cf_type="
response = requests.get(url_global)

# Transform to json

data = response.json()

# Convert json to DataFramedat.(

data_global = pd.DataFrame(data['items'])

# Request to API for refugee data in Germany from 1951 to 2022

url_DEU = "https://api.unhcr.org/population/v1/population/?page=&limit=1000&yearFrom=1951&yearTo=2022&year=&download=&coo=&coa=GFR&coo_all=&coa_all=&cf_type="
response = requests.get(url_DEU)

# Transform to json

data = response.json()

# Convert json to DataFrame

data_DEU = pd.DataFrame(data['items']).sort_values(by = 'year')

# Request to API for refugee data in Germany from 2022 and the country fo origin

url_DEU_latest = "https://api.unhcr.org/population/v1/population/?page=&limit=1000&yearFrom=&yearTo=&year=2022&download=&coo=&coa=GFR&coo_all=true&coa_all=&cf_type="
response = requests.get(url_DEU_latest)

# Transform to json

data = response.json()

# Convert json to DataFrame

data_DEU_latest = pd.DataFrame(data['items'])

##### Add population data to global data #####

# Create empty dictionary to merge data

population_dict = {}

# Create dictionary with ISO-Code and Population

for country in data_global['coa_iso'].values:
    population_dict[country] = pypopulation.get_population_a3(country)

# Create new colum and map population to ISO-Code

data_global['Bevölkerungszahl'] = data_global['coa_iso'].map(population_dict).fillna(0).astype(int)
data_DEU_latest['Bevölkerungszahl'] = data_global['coa_iso'].map(population_dict).fillna(0).astype(int)

# Create variable with german population

population_germany = data_global.loc[data_global[data_global['coa_iso'] == 'DEU'].index.values.astype(int)[0]]['Bevölkerungszahl']

##### Translate Dataframes into german #####

### Translate name of colums in dataframes ###

data_global.rename(columns={'year':'Jahr', 'coa_iso':'Asylstaat', "refugees": 'Geflüchtete unter UNHCR Mandat'},
                   inplace=True)

data_DEU.rename(columns={'year':'Jahr', 'coa_iso':'Asylstaat', "refugees": 'Geflüchtete unter UNHCR Mandat'},
                inplace=True)

data_DEU_latest.rename(columns={'year':'Jahr', 'coa_iso':'Asylstaat','coo_iso':'Herkunftsland',
                                "refugees": 'Geflüchtete unter UNHCR Mandat'},
                       inplace=True)

# Import CSV with countrycodes

data_countrycodes = pd.read_csv('data/countrycodes.csv')

# Write country names in a list (english and german)

countrycodes = data_countrycodes['ISO 3166-1 alpha3'].tolist()
countrynames_german = data_countrycodes['Country (de)'].tolist()

# Create dictionary from country_lists

countrynames_englishToGerman = {}
for key in countrycodes:
    for value in countrynames_german:
        countrynames_englishToGerman[key] = value
        countrynames_german.remove(value)
        break

# translate all countries in dataframes

data_global = data_global.replace({'Asylstaat': countrynames_englishToGerman})
data_DEU = data_DEU.replace({'Asylstaat': countrynames_englishToGerman})
data_DEU_latest = data_DEU_latest.replace({'Asylstaat': countrynames_englishToGerman})
data_DEU_latest = data_DEU_latest.replace({'Herkunftsland': countrynames_englishToGerman})

##### Clean data #####
### Clean global data ###

data_global.drop(['coo_id', 'coo_name', 'coo', 'coo_iso', 'coa_id', 'coa_name', 'coa', 'asylum_seekers',
                  'returned_refugees', 'idps', 'returned_idps', 'stateless', 'ooc', 'oip', 'hst'],
                 axis=1, inplace=True)

### Clean DEU data ###

data_DEU.drop(['coo_id', 'coo_name', 'coo', 'coo_iso', 'coa_id', 'coa_name', 'coa', 'asylum_seekers',
                  'returned_refugees', 'idps', 'returned_idps', 'stateless', 'ooc', 'oip', 'hst'],
                 axis=1, inplace=True)

### Clean DEU data latest ###

data_DEU_latest.drop(['coo_id', 'coo_name', 'coo', 'coa_id', 'coa_name', 'coa', 'asylum_seekers',
                  'returned_refugees', 'idps', 'returned_idps', 'stateless', 'ooc', 'oip', 'hst'],
                 axis=1, inplace=True)

### Convert columns with int from object to int

data_global = data_global.astype({'Geflüchtete unter UNHCR Mandat': 'int'})
data_DEU = data_DEU.astype({'Geflüchtete unter UNHCR Mandat': 'int'})
data_DEU_latest = data_DEU_latest.astype({'Geflüchtete unter UNHCR Mandat': 'int'})


### Rename NaN.Value in data_global

data_DEU_latest['Herkunftsland'] = data_DEU_latest['Herkunftsland'].replace({None: 'Herkunftsland unbekannt'})
data_DEU_latest['Herkunftsland'] = data_DEU_latest['Herkunftsland'].replace({'XXA': 'Staatenlos'})


########### Graphs for Dashboard ###########

# Load textfiles for website - Question 1

with open('text/introduction_1.txt') as f:
    introduction_1 = f.readlines()

with open('text/introduction_2.txt') as f:
    introduction_2 = f.readlines()

with open('text/introduction_3.txt') as f:
    introduction_3 = f.readlines()

### Question 1: How many refugees came to Germany since 1970?

data_DEU_from1970 = data_DEU.drop(data_DEU.index[0:19])

#Create line graph with plotly
fig_question1 = px.line(data_DEU_from1970, x='Jahr', y="Geflüchtete unter UNHCR Mandat")

#Create title and make it bold
fig_question1.update_layout(title="<b>Wie viele Geflüchtete sind seit 1970 nach Deutschland gekommen?</b>")

#Set colour and width for line graph
fig_question1.update_traces(line_color='#fc8a1b', line_width=2)

#Change text font color and size, align text and change backgroundcolor
fig_question1.update_layout(
    font_family="Helvetica",
    font_color="black",
    font_size=14,
    title_font_family="Helvetica",
    title_font_color="black",
    title_font_size=22,
    legend_title_font_color="black",
    title_x=0.5,
    plot_bgcolor="#e0e0e0"
)

#Add source
fig_question1.add_annotation(
    dict(font=dict(size=12),
    x=0,
    y=-0.17,
    showarrow=False,
    text="Quelle: UNHCR",
    xanchor='left',
    xref="paper",
    yref="paper")
)

# Load textfiles for website - Question 1

with open('text/question1_1.txt') as f:
    question1_1 = f.readlines()

### Question 2: Where do the most refugees come from?

# Create new data set of top 10 countries sorted by numbers of refugees

most_refugees_in_GER = data_DEU_latest.sort_values(by="Geflüchtete unter UNHCR Mandat", ascending=False).head(n=10)

#Create bar graph with plotly

fig_question2 = px.bar(most_refugees_in_GER, x='Herkunftsland', y="Geflüchtete unter UNHCR Mandat")

#Create title and make it bold
fig_question2.update_layout(title="<b>Aus welchen Herkunftsländern stammen die meisten Geflüchteten?</b>")

#Set colour and width for line graph
fig_question2.update_traces(marker_color='#fc8a1b')

#Align title
fig_question2.update_layout(title_x=0.5)

#Change text font color and size, align text and change backgroundcolor
fig_question2.update_layout(
    font_family="Helvetica",
    font_color="black",
    font_size=14,
    title_font_family="Helvetica",
    title_font_color="black",
    title_font_size=22,
    legend_title_font_color="black",
    title_x=0.5,
    plot_bgcolor="#e0e0e0"
)

#Add source
fig_question2.add_annotation(
    dict(font=dict(size=12),
    x=0,
    y=-0.38,
    showarrow=False,
    text="Quelle: UNHCR",
    xanchor='left',
    xref="paper",
    yref="paper")
)

# Load textfiles for website - Question 2

with open('text/question2_1.txt') as f:
    question2_1 = f.readlines()

with open('text/question2_2.txt') as f:
    question2_2 = f.readlines()

### Question 3: What percentage of the German populations are refugees?

# restore list with German country names for dropdown

countrynames_german = data_countrycodes['Country (de)'].tolist()

# define function to calculate percentage

def percentage_of_population(country, df):
    country_of_origin = df[df["Herkunftsland"] == country]["Geflüchtete unter UNHCR Mandat"]
    return country_of_origin / population_germany * 100

number_refugees_Germany = None

### Question 4: Which countries in the world receive the most refugees? (Compared to Germany)

#Sort data_global by top 10 countries who have accepted the most refugees in 2022

top10_asylumstates_global=data_global.sort_values(by=["Geflüchtete unter UNHCR Mandat"], ascending=[False]).head(n=10)

#Create bar graph with plotly

fig_question4 = px.bar(top10_asylumstates_global, x='Asylstaat', y="Geflüchtete unter UNHCR Mandat")

#Create title and make it bold
fig_question4.update_layout(title="<b>Wie viele Geflüchtete nimmt Deutchland" + "<br>" + "im Vergleich zur Welt auf? (Stand: 2022)</b>")

#Set colour and width for line graph
fig_question4.update_traces(marker_color='#fc8a1b')

#Align title
fig_question4.update_layout(title_x=0.5)

#Change text font color and size, align text and change backgroundcolor
fig_question4.update_layout(
    font_family="Helvetica",
    font_color="black",
    font_size=14,
    title_font_family="Helvetica",
    title_font_color="black",
    title_font_size=22,
    legend_title_font_color="black",
    title_x=0.5,
    plot_bgcolor="#e0e0e0"
)

#Add source
fig_question4.add_annotation(
    dict(font=dict(size=12),
    x=0,
    y=-0.17,
    showarrow=False,
    text="Quelle: UNHCR",
    xanchor='left',
    xref="paper",
    yref="paper")
)

# Load textfiles for website - Question 4

with open('text/question4_1.txt', encoding='utf-8') as f:
    question4_1 = f.readlines()

with open('text/question4_2.txt', encoding='utf-8') as f:
    question4_2 = f.readlines()

with open('text/question4_3.txt', encoding='utf-8') as f:
    question4_3 = f.readlines()

########## Build Website ##########

### Start Dash ###

app = dash.Dash()

### Callback for dropdown

# Start app callback for dropdown

@app.callback(
    Output('dd-output-container', 'children'),
    Input('demo-dropdown', 'value')
)

# Define outputfunction for dropdown

def update_output(selected_country):
    number_refugees_Germany = data_DEU_latest[data_DEU_latest["Herkunftsland"] == selected_country]["Geflüchtete unter UNHCR Mandat"]
    number_refugees_Germany = number_refugees_Germany.tolist()
    number_refugees_Germany = number_refugees_Germany[0]
    percentage_country_of_origin = percentage_of_population(selected_country, data_DEU_latest)
    percentage_country_of_origin = percentage_country_of_origin.tolist()
    percentage_country_of_origin = round(percentage_country_of_origin[0], 4)
    automated_text = f'In Deutschland leben {number_refugees_Germany} Geflüchtete aus {selected_country}. Das sind {percentage_country_of_origin} Prozent der deutschen Bevölkerung.'
    return automated_text

### Website Layout ###

app.layout = html.Div(children=[
    # Headline
    html.H1(id='headline', children='Flucht nach Deutschland',
            style={'textAlign': 'center', 'marginTop': 40, 'marginBottom': 10, 'font-family': 'Roboto'}),
    html.H3(id='subheadline', children='Eine Verhältnisrechnung',
            style={'textAlign': 'center', 'marginTop': 10, 'marginBottom': 10, 'font-family': 'Roboto'}),
    html.H4(id='authors', children='Von Alina Eckelmann, Annika Franz, Justus Niebling und Albert Lich',
            style={'textAlign': 'center', 'marginTop': 10, 'marginBottom': 40, 'font-family': 'Roboto'}),
    # Introductiontext
    html.Div([
        html.H4(introduction_1,
                style={'textAlign': 'justified', 'margin': '10px 25% 0% 25%', 'font-family': 'Roboto',
                       'line-height': '130%'}),
        html.H4(introduction_2,
                style={'textAlign': 'justified', 'margin': '5px 25% 10px 25%', 'font-family': 'Roboto', 'line-height': '130%'}),
        html.Div(introduction_3,
                style={'textAlign': 'justified', 'margin': '5px 25% 40px 25%', 'font-family': 'Roboto', 'line-height': '130%', 'font-size': '80%'})
    ]),

    # Question 1: How many refugees came to Germany since 1970?
    html.Div([
        dcc.Graph(figure=fig_question1, style={'margin' : '10px 25% 40px 25%'}),
        html.H4(children='Ein Blick auf Deutschland:',
            style={'textAlign': 'justified', 'margin' : '10px 25% 10px 25%', 'font-family': 'Roboto'}),
        html.H4(question1_1,
                style={'textAlign': 'justified', 'margin' : '10px 25% 40px 25%', 'font-family': 'Roboto', 'line-height': '130%'}),
    ]),

    # Question 2: Where do the most refugees come from?
    html.Div([
        dcc.Graph(figure=fig_question2, style={'margin' : '10px 25% 30px 25%'}),
        html.H4(question2_1,
                style={'textAlign': 'justified', 'margin' : '10px 25% 20px 25%', 'font-family': 'Roboto', 'line-height': '130%'}),
        html.H4(question2_2,
                style={'textAlign': 'justified', 'margin' : '10px 25% 40px 25%', 'font-family': 'Roboto', 'line-height': '130%'}),
        # Question 3: What percentage of the German populations are refugees?
        dcc.Dropdown(countrynames_german, id='demo-dropdown', placeholder="Wählen Sie ein Herkunftsland",
                     style={'align': 'left', 'margin' : '10px 33% 20px 16.5%', 'font-family': 'Roboto'}),
        html.H4(id='dd-output-container',
                 style={'align': 'left', 'margin' : '10px 25% 40px 25%', 'font-family': 'Roboto'}),
    ]),

    # Question 4: Which countries in the world receive the most refugees? (Compared to Germany)
    html.Div([
        dcc.Graph(figure=fig_question4, style={'margin' : '10px 25% 20px 25%'}),
        html.H4(question4_1,
                style={'textAlign': 'justified', 'margin' : '10px 25% 0% 25%', 'font-family': 'Roboto', 'line-height': '130%'}),
        html.H4(question4_2,
                style={'textAlign': 'justified', 'margin' : '5px 25% 0% 25%', 'font-family': 'Roboto', 'line-height': '130%'}),
        html.H4(question4_3,
                style={'textAlign': 'justified', 'margin' : '5px 25% 5% 25%', 'font-family': 'Roboto', 'line-height': '130%'})
    ])
])

### Run Dash ###

if __name__ == '__main__':
    app.run_server()