from ssl import CHANNEL_BINDING_TYPES
import time
start_time = time.time()
import geopandas
import pandas as pd
import folium
import os
import branca
import numpy as np
import json
from selenium import webdriver
from selenium.webdriver.common.keys import Keys 
# Source: https://selenium-python.readthedocs.io/getting-started.html
import PIL.Image
import IPython

def create_map(tile_option = None, starting_zoom = 6, 
starting_location = [38.7, -95], save_path = 'pub_domain_features_map_smaller',
gdf_water = None, gdf_states = None, gdf_places = None, gdf_roads = None,
include_cities = True):

    pub_domain_features_map = folium.Map(location=starting_location, 
    zoom_start=starting_zoom, tiles = tile_option)
    # tiles can be set to 'None' in order to produce a map without any 
    # background details. This produces a cleaner static image.

    # Although Folium has a choropleth library, I wasn't able to find a way
    # to disable the default legend. Therefore, I am instead using a custom
    # choropleth mapping function. Much of this function is based on 
    # Amodiovalerio Verde's code at:
    # https://vverde.github.io/blob/interactivechoropleth.html . 


    # Adding in bodies of water:
    print("Adding in bodies of water:")

    water_style_function = lambda x: {
                "weight": 0.5,
                'color': '#0000FF',
                'fillOpacity': 1}
            # This style function will plot the bodies of water in
            # major_us_water_bodies as opaque blue polygons.

    folium.features.GeoJson(gdf_water, name = 'Bodies of Water',
        style_function=water_style_function).add_to(pub_domain_features_map)

    # Adding in states:
    print("Adding in states:")
    states_style_function = lambda x: {
                "weight": 1,
                'color': '#000000',
                'fillOpacity': 0}
            # This style function will plot the bodies of water in
            # major_us_water_bodies as opaque blue polygons.

    folium.features.GeoJson(gdf_states, name = 'States',
        style_function=states_style_function).add_to(pub_domain_features_map)

    # Adding in places:
    print("Adding in roads:")

    roads_style_function = lambda x: {
                "weight": 1,
                'color': '#777777',
                'fillOpacity': 0}
            # This style function will plot the bodies of water in
            # major_us_water_bodies as opaque blue polygons.

    folium.features.GeoJson(gdf_roads, name = 'Roads',
        style_function=roads_style_function).add_to(pub_domain_features_map)

    # Adding in cities:
    if include_cities == True:
        print("Adding in cities:")
        place_feature_group = folium.FeatureGroup(name = 'Cities')
        name_feature_group = folium.FeatureGroup(name = 'City Names')
        # This style tag will allow me to control some basic style
        # properties of each diocese's name.
        style_tag = '<style> p{color:black; line-height: 1} </style>'
        # Based on https://developer.mozilla.org/en-US/docs/Web/HTML/Element/style
        for i in range(len(gdf_places)):
            city_name = gdf_places.iloc[i, gdf_places.columns.get_loc('place_name')]
            place_coords = [gdf_places.iloc[i, gdf_places.columns.get_loc('INTPTLAT')
            ], gdf_places.iloc[i, gdf_places.columns.get_loc('INTPTLONG')]]
            folium.CircleMarker(place_coords, fill = True, radius = 5, 
            color = '#FF0000', fill_opacity = 0.8, stroke = False).add_to(place_feature_group)
            folium.Marker(place_coords, icon = folium.DivIcon(
            icon_anchor=(0, 0), 
                html=f"{style_tag}<p><b>{city_name}<b></p>")
                ).add_to(name_feature_group)
            # See https://python-visualization.github.io/folium/modules.html#folium.vector_layers.path_options
            # for Circle options.
            # Note that, if the stroke is set to True, then the circles
            # may appear solid even if the fill_opacity is set below 1.
            # That's because the default stroke width is large enough
            # to fill up the whole marker.
        place_feature_group.add_to(pub_domain_features_map) 
        name_feature_group.add_to(pub_domain_features_map) 


    folium.LayerControl().add_to(pub_domain_features_map) # This allows the user
    # to select which layers of the map (provinces, cathedrals, diocese names,
    # etc. to display.)
    print("Saving map:")
    pub_domain_features_map.save(save_path+'.html')


def create_map_screenshot(absolute_path_to_map_folder, 
map_name, added_text = '', screenshot_save_path = None):

    '''
    This function uses the Selenium library to create a screenshot 
    of a map so that it can be shared as a .png file.
    See https://www.selenium.dev/documentation/ for more information on 
    Selenium. 
    
    absolute_path_to_map_folder designates the absolute path where
    the map is stored. (I wasn't able to get this code to work using
    just relative paths.) 

    map_name specifies the name of the map, including its extension.

    screenshot_save_path designates the folder where you wish to save
    the map screenshot. This can be a relative path.

    Note that some setup work is required for the Selenium code
    to run correctly; if you don't have time right now to complete this 
    setup, you can comment out any code that calls this function.
    '''

    ff_driver = webdriver.Firefox() 
    # See https://www.selenium.dev/documentation/webdriver/getting_started/open_browser/
    # For more information on using Selenium to get screenshots of .html 
    # files, see my get_screenshots.ipynb file within my route_maps_builder
    # program, available here:
    # https://github.com/kburchfiel/route_maps_builder/blob/master/get_screenshots.ipynb
    window_width = 3000 # This produces a large window that can better
    # capture small details (such as zip code shapefiles).
    ff_driver.set_window_size(window_width,window_width*(9/16)) # Creates
    # a window with an HD/4K/8K aspect ratio
    ff_driver.get(f'{absolute_path_to_map_folder}\\{map_name}') 
    # See https://www.selenium.dev/documentation/webdriver/browser/navigation/
    time.sleep(2) # This gives the page sufficient
    # time to load the map tiles before the screenshot is taken. 
    # You can also experiment with longer sleep times.

    if screenshot_save_path != None:
        # If specifying a screenshot save path, you must create this path
        # within your directory before the function is run; otherwise,
        # it won't return an image. 
        ff_driver.get_screenshot_as_file(
            screenshot_save_path+'/'+map_name.replace(
                '.html','')+added_text+'.png') 
    else: # If no save path was specified for the screenshot, the image
        # will be saved within the project's root folder.
        ff_driver.get_screenshot_as_file(
            map_name.replace('.html','')+added_text+'.png') 
    # Based on:
    # https://www.selenium.dev/selenium/docs/api/java/org/openqa/selenium/TakesScreenshot.html

    ff_driver.quit()
    # Based on: https://www.selenium.dev/documentation/webdriver/browser/windows/

def convert_png_to_smaller_jpg(png_folder, png_image_name, jpg_folder, 
reduction_factor = 1, quality_factor = 50):
    ''' This function converts a .png image into a smaller .jpg image, which
    helps reduce file sizes and load times when displaying a series of images
    within a notebook or online.
    png_folder and png_image_name specify the location of the original .png
    image.
    jpg folder specifies the location where the .jpg screenshot should be
    saved.
    reduction_factor specifies the amount by which you would like to reduce
    the image's dimensions. For instance, to convert a 4K (3840*2160) image
    to a full HD (1920*1080) one, use a reduction factor of 2. If you do not
    wish to reduce the image's size, use the default reduction factor of 1.
    '''
    with PIL.Image.open(f'{png_folder}/{png_image_name}') as map_image:
        (width, height) = (map_image.width // reduction_factor, 
        map_image.height // reduction_factor)
        jpg_image = map_image.resize((width, height))
        # The above code is based on:
        # https://pillow.readthedocs.io/en/stable/reference/Image.html
        jpg_image = jpg_image.convert('RGB')
        # The above conversion is necessary in order to save .png files as 
        # .jpg files. It's based on Patrick Artner's answer at: 
        # https://stackoverflow.com/a/48248432/13097194
        jpg_image_name = png_image_name.replace('png', 'jpg') 
        jpg_image.save(f'{jpg_folder}/{jpg_image_name}',
        format = 'JPEG', quality = quality_factor, optimize = True)
        # See https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#jpeg

def add_alaska_and_hawaii(starting_map_name, tile_option = 'Stamen Toner',
absolute_path_to_map_folder = '', gdf_water = None,
gdf_states = None, gdf_places = None, gdf_roads = None, include_cities = True):
    '''This function creates a static version of the map stored at
    starting_map_name.html that includes Alaska and Hawaii at the bottom left.
    The value of starting_map_name should not include the .html at the end. 
    E.g. pass revised_diocese_map as an argument rather than 
    revised_diocese_map.html.
    This function assumes that starting_map_name.html was produced using 
    generate_diocese_map() with a starting zoom of 6 and a starting location
    of [38.7, -95] (the default parameters for generate_diocese_map().) It also
    assumes that a .png screenshot of that map was already created using
    create_map_screenshot().

    This function performs the following tasks:
    1. Creates .HTML maps of Alaska and Hawaii. (These are the same as the maps 
    created above except that they are centered near Alaska and Hawaii).
    2. Saves these maps as screenshots, then creates cropped versions
    of the screenshots that focus  on each state.
    3. Loads the screenshot of a map specified by 'starting_map_name'; 
    pastes the cropped Alaska and Hawaii images in at the bottom left corner;
    and saves this new screenshot.  

    Note that the names of the additional maps and screenshots 
    created within this function are based off starting_map_name.
    ''' 

    # Part 1: Creating Alaska map, screenshot, and cropped screenshot
    create_map(tile_option = tile_option, starting_zoom = 4, 
    starting_location = [65, -150], save_path = starting_map_name+'_alaska',
    gdf_water = gdf_water, gdf_states = gdf_states, 
    gdf_places = gdf_places, gdf_roads = gdf_roads, include_cities = include_cities)
    # This method of creating an Alaska-centric map is admittedly very
    # inefficient, as it also generates all other parts of the map.
    # Another option would be to use Selenium to navigate to Alaska and then
    # take the screenshot from there, but I had trouble finding a way to
    # get that to work. Therefore, I'll create extra .HTML maps instead.
    # You may choose to delete these extra .HTML maps, since they are only
    # used for screenshot generation.
    create_map_screenshot(absolute_path_to_map_folder = \
        absolute_path_to_map_folder, 
        map_name = starting_map_name+'_alaska.html', 
        screenshot_save_path = 'screenshots')
    os.remove(starting_map_name+'_alaska.html') # This .HTML 
    # file is no longer needed, so it can be removed to save
    # file space.
    # https://docs.python.org/3/library/os.html
    with PIL.Image.open(
        'screenshots/'+starting_map_name+'_alaska.png') as map_image:
        # See https://pillow.readthedocs.io/en/stable/reference/Image.html
        print("Opened")
        cropped_image = map_image.crop((2200, 1100, 3500, 2300)) # Crops the
        # map based on the specified left, upper, right, and lower points. See
        # https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.crop
        # As with other parts of this program, these points were determined
        # using trial and error.
        # display(cropped_image) # https://stackoverflow.com/a/26649884/13097194
        # Useful for debugging
        cropped_image.save(
            'screenshots/'+starting_map_name+'_alaska_cropped.png')


    # Part 2: Creating Hawaii map, screenshot, and cropped screenshot
    create_map(tile_option = tile_option, starting_zoom = 6, 
    starting_location = [21, -156], save_path = starting_map_name+'_hawaii',
    gdf_water = gdf_water, gdf_states = gdf_states,
    gdf_places = gdf_places, gdf_roads = gdf_roads, 
    include_cities = include_cities)
    create_map_screenshot(absolute_path_to_map_folder = \
        absolute_path_to_map_folder, 
        map_name = starting_map_name+'_hawaii.html', 
        screenshot_save_path = 'screenshots')
    os.remove(starting_map_name+'_hawaii.html')
    with PIL.Image.open(
        'screenshots/'+starting_map_name+'_hawaii.png') as map_image:
        print("Opened")
        cropped_image = map_image.crop((2500, 1400, 3300, 1900)) 
        cropped_image.save(
            'screenshots/'+starting_map_name+'_hawaii_cropped.png')

    
    # Part 3: Pasting these screenshots into the original map 
    with PIL.Image.open('screenshots/'+starting_map_name+'.png') as map_image:
        alaska = PIL.Image.open(
            'screenshots/'+starting_map_name+'_alaska_cropped.png')
        alaska = alaska.resize(
            (int(alaska.width/1.25), int(alaska.height/1.25)))
        hawaii = PIL.Image.open(
            'screenshots/'+starting_map_name+'_hawaii_cropped.png')
        # The following lines paste the cropped Alaska and Hawaii maps
        # onto starting_map_name.png.
        map_image.paste(im = alaska, box = (0, 2300))
        map_image.paste(im = hawaii, box = (1200, 2600))
        map_image.save('screenshots/'+starting_map_name+'_50_states.png')

