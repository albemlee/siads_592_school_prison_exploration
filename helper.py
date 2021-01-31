import requests
import json
import pandas as pd
import numpy as np
import geopandas as gpd
import folium
import branca.colormap as cm
from datetime import date, datetime
import pandas_bokeh

from bokeh.models import *
from bokeh.plotting import *
from bokeh.io import *
from bokeh.tile_providers import *
from bokeh.palettes import *
from bokeh.transform import *
from bokeh.layouts import *
from bokeh.models import ColumnDataSource

import warnings
warnings.filterwarnings('ignore')

class EducationData_API:
    def __init__(self):
        self.finance_keep_col = [
            'exp_current_supp_serve_total',
            'exp_current_other',
            'exp_current_food_serv',
            'enrollment_fall_responsible',
            'enrollment_fall_school',
            'salaries_total',
            'rev_fed_total',
            'salaries_food_service',
            'benefits_supp_sch_admin',
            'exp_current_sch_admin',
            'rev_fed_child_nutrition_act',
            'salaries_supp_bco',
            'rev_total',
            'exp_current_elsec_total',
            'salaries_teachers_regular_prog',
            'rev_state_total',
            'exp_total',
            'salaries_supp_sch_admin',
            'exp_current_bco',
            'rev_state_gen_formula_assist',
            'salaries_supp_operation_plant',
            'exp_current_operation_plant',
            'salaries_instruction',
            'rev_fed_state_title_i',
            'exp_current_instruction_total',
            'rev_fed_state_idea',
            'benefits_employee_total',
            'benefits_supp_bco',
            'debt_longterm_outstand_beg_fy',
            'debt_longterm_outstand_end_fy',
            'rev_local_total',
            'benefits_supp_operation_plant',
            'rev_fed_nonspec',
            'payments_private_schools',
            'salaries_teachers_vocational',
            'payments_charter_schools',
            'rev_state_bilingual_ed',
            'rev_state_gifted_talented',
            'exp_utilities_energy',
            'rev_state_vocational_ed',
            'rev_local_dist_activ_receipts',
            'assets_sinking_fund'
        ]

    def get_request(self, topic, source, endpoint, year):
        self.topic = topic
        self.source = source
        self.endpoint = endpoint
        self.year = year
        self.base_url = 'https://educationdata.urban.org/api/v1/{}/{}/{}/{}/'.format(
            self.topic,
            self.source,
            self.endpoint,
            self.year
        )
        results = []
        api_response = requests.get(url = self.base_url)
        results.extend(api_response.json()['results'])
        next_page = api_response.json()['next']
        while next_page:
            api_response = requests.get(url = next_page)
            results.extend(api_response.json()['results'])
            next_page = api_response.json()['next']

        self.results_df = pd.DataFrame(results)

    def merge_ccd(self, year):
        if year >= 1994 and year <= 2016:
            finance_df = pd.read_csv('data/ccd_finance/{}_finance.csv'.format(year))
            finance_df = finance_df[['leaid'] + self.finance_keep_col]
            directory_df = pd.read_csv('data/ccd_directory/{}_directory.csv'.format(year), dtype=str)
            directory_df = directory_df[
                [
                    'leaid',
                    'county_code',
                    'fips'
                ]
            ]

            directory_df['county_code'] = directory_df['county_code'].apply(
                lambda x:
                '0{}'.format(x) if len(str(x)) == 4 else str(x)
            )
            directory_df['fips'] = directory_df['fips'].apply(
                lambda x:
                '0{}'.format(str(x).split('.')[0])
                if len(str(x).split('.')[0]) == 1 else str(x).split('.')[0]
            )
            directory_df['state'] = directory_df['county_code'].apply(
                lambda x:
                x[:2]
            )

        return finance_df.merge(directory_df, how='left', left_on='leaid', right_on='leaid')

    def group_ccd(self, year, level = 'county_code'):
        merged_df = self.merge_ccd(year)
        merged_df = merged_df[[level] + self.finance_keep_col]

        # doesn't handle NA values
        return merged_df.groupby(level).median()

class map_generator():
    def latitudes(self, df):
        lats = []
        for row in df['county_centroid']:
            row = row.split()[1:3]
            row[0] = row[0].strip("(")
            row[1] = row[1].strip(")")
            row[0] = float(row[0])
            row[1] = float(row[1])
            lats.append(row[0])
        return lats 

    def longitudes(self, df):
        longs = []
        for row in df['county_centroid']:
            row = row.split()[1:3]
            row[0] = row[0].strip("(")
            row[1] = row[1].strip(")")
            row[0] = float(row[0])
            row[1] = float(row[1])
            longs.append(row[1])
        return longs

    ## Function to merge the data frame (MUST HAVE 'FIPS_Code' column) with the map of U.S. counties.

    def FIPS_Code_merge(self, df):
        fname = 'data/CountyShapeFile/cb_2018_us_county_500k.shp'
        SHAPE = gpd.read_file(fname)
        SHAPE['FIPS_Code'] = SHAPE['STATEFP'].astype(str) + SHAPE['COUNTYFP'].astype(str)
        SHAPE['FIPS_Code'] = SHAPE['FIPS_Code'].astype('int64')
        merged_df = SHAPE.merge(df,on="FIPS_Code")

        if 'geometry_x' in list(merged_df.columns):
            merged_df = merged_df.rename(columns={'geometry_x':'geometry'})


        merged_df['county_centroid'] = merged_df['geometry'].centroid.astype(str)
        merged_df['latitude'] = self.latitudes(merged_df)
        merged_df['longitude'] = self.longitudes(merged_df)

        merged_df = merged_df[
            (merged_df['latitude'] <= -60) & 
            (merged_df['latitude'] >= -130) & 
            (merged_df['longitude'] <= 50) & 
            (merged_df['longitude'] >= 20)
        ]

        return merged_df

    def getmap_with_year(
        self, 
        df, 
        year,
        county_name_column, 
        variable_column, 
        colors, 
        low, 
        high, 
        title
    ):
        '''
        param df pandas.DataFrame: Name of the data frame
        param year int: The year of interest (there is also a version for data frames without years)
        param county_name_column string: The name of the counties as per the data frame
        param variable_column string: The variable of interest in the data frame
        param colors str: Choice of color scheme from Color Brewer palette https://rdrr.io/cran/RColorBrewer/man/ColorBrewer.html 
        param low float: The min of the color scheme 
        param high float: The max of the color scheme
        param title string: The title of the map
        '''
        df = self.FIPS_Code_merge(df)
        df['year'] = df['year'].astype(int)
        df = df[df['year']==year]

        jsonify = json.loads(df.to_json())
        json_data = json.dumps(jsonify)
        geosource = GeoJSONDataSource(geojson = json_data)

        #set the color palette 
        palette = brewer[colors][8]
        palette = palette[::-1]
        color_mapper = LinearColorMapper(
            palette = palette, 
            low = low, 
            high = high,  
            nan_color = '#d9d9d9'
        )
        color_bar = ColorBar(
            color_mapper=color_mapper, 
            label_standoff=8,
            width = 500, 
            height = 20,
            border_line_color='black',
            location = (0,0), 
            orientation ='horizontal'
        )

        #Set the size and title of the graph
        p = figure(
            title = title, 
            plot_height = 700 , 
            plot_width = 1000, 
            toolbar_location = None, 
            tooltips=[
                ("County", "@"+county_name_column),
                ("Year","@year"),
                (variable_column, "@"+variable_column)
            ]
        )

        #Makes it so there are no gird lines
        p.xgrid.grid_line_color = None
        p.ygrid.grid_line_color = None
        p.patches(
            'xs',
            'ys', 
            source = geosource,
            fill_color = {
                'field': variable_column, 
                'transform' : color_mapper
            },
            line_color = 'black', 
            line_width = 0.25, 
            fill_alpha = 1
        )
        p.add_layout(
            color_bar, 
            'below'
        )

        output_notebook()
        return show(p)
    
    def getmap(
        self, 
        df, 
        county_name_column,
        variable_column, 
        colors, 
        low, 
        high, 
        title
    ):
        '''
        param df pandas.DataFrame: Name of the data frame
        param county_name_column string: The name of the counties as per the data frame
        param variable_column string: The variable of interest in the data frame
        param colors str: Choice of color scheme from Color Brewer palette https://rdrr.io/cran/RColorBrewer/man/ColorBrewer.html 
        param low float: The min of the color scheme 
        param high float: The max of the color scheme
        param title string: The title of the map
        '''
        df = self.FIPS_Code_merge(df)

        jsonify = json.loads(df.to_json())
        json_data = json.dumps(jsonify)
        geosource = GeoJSONDataSource(geojson = json_data)

        #set the color palette 
        palette = brewer[colors][8]
        palette = palette[::-1]
        color_mapper = LinearColorMapper(palette = palette, low = low, high = high,  nan_color = '#d9d9d9')
        color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8,width = 500, height = 20,
        border_line_color='black',location = (0,0), orientation ='horizontal')

        #Set the size and title of the graph
        p = figure(
            title = title, 
            plot_height = 700 , 
            plot_width = 1000, 
            toolbar_location = None, 
            tooltips=[
                ("County", "@"+county_name_column),
                (variable_column, "@"+variable_column)
            ]
        )

        #Makes it so there are no gird lines
        p.xgrid.grid_line_color = None
        p.ygrid.grid_line_color = None
        p.patches(
            'xs',
            'ys', 
            source = geosource,
            fill_color = {
                'field': variable_column, 
                'transform': color_mapper
            },
            line_color = 'black', 
            line_width = 0.25, 
            fill_alpha = 1
        )
        p.add_layout(color_bar, 'below')

        output_notebook()
        return show(p)
    
    def savemap_with_year(
        self, 
        df, 
        year,
        county_name_column, 
        variable_column, 
        colors, 
        low, 
        high, 
        title, 
        filename
    ):
        df = self.FIPS_Code_merge(df)
        df['year'] = df['year'].astype(int)
        df = df[df['year']==year]

        jsonify = json.loads(df.to_json())
        json_data = json.dumps(jsonify)
        geosource = GeoJSONDataSource(geojson = json_data)

        #set the color palette 
        palette = brewer[colors][8]
        palette = palette[::-1]
        color_mapper = LinearColorMapper(palette = palette, low = low, high = high,  nan_color = '#d9d9d9')
        color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8,width = 1000, height = 50,
        border_line_color='black',location = (0,0), orientation ='horizontal')

        #Set the size and title of the graph
        p = figure(title = title, plot_height = 1400 , plot_width = 2000, toolbar_location = None, 
              tooltips=[
             ("County", "@"+county_name_column),
             ("Year","@year"),
             (variable_column, "@"+variable_column)])

        #Makes it so there are no gird lines
        p.xgrid.grid_line_color = None
        p.ygrid.grid_line_color = None
        p.patches('xs','ys', source = geosource,fill_color = {'field'     :variable_column, 'transform' : color_mapper},
             line_color = 'black', line_width = 0.25, fill_alpha = 1)
        p.add_layout(color_bar, 'below')
        filename = filename
        output_notebook()
        return export_png(p, filename=filename)