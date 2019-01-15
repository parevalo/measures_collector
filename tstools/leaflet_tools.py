# Functions for interacting with ipyleaflet
import ee
import ipyleaflet
import tstools.utils as utils

# Make a leaflet map
def make_map(zoom, layout, center, dragging=True, class_popup_on_click=False,
             basemap=ipyleaflet.basemaps.Esri.WorldStreetMap):

    m = ipyleaflet.Map(zoom=zoom, layout=layout, center=center, dragging=dragging,
                       close_popup_on_click=False, basemap=basemap)

    return m

# Add a basemap
def add_basemap(m, basemap):

    bm = ipyleaflet.basemap_to_tiles(basemap)
    m.add_layer(bm)

    return

# Add draw control
def add_draw_control(marker, m, polygon={}, circle={}, circlemarker={}, polyline={}, function=None):

    dc = ipyleaflet.DrawControl(marker=marker, polygon=polygon, circlemarker=circlemarker,
                                polyline=polyline)

    if function is not None:
        dc.on_draw(function)

    m.add_control(dc)

    return m

# Add sample point to map
def add_map_point(data, zoom, m, kml, name):

    # Make geojson from data
    gjson = ipyleaflet.GeoJSON(data=data, name=name)

    # Center map
    m.center = gjson.data['coordinates'][::-1]

    # Set map zoom
    m.zoom = zoom

    # Add geojson to map
    m.add_layer(gjson)

    # Make KML via earth engine functionality
    geo_point = ee.Geometry.Point(gjson.data['coordinates'][::-1]) # This may not work
    geo_fc = ee.FeatureCollection(geo_point)
    kmlstr = geo_fc.getDownloadURL("kml")

    # Update KML widget
    kml.value = "<a '_blank' rel='noopener noreferrer' href={}>KML Link</a>".format(kmlstr)

    return

# Clear all layers on map
def clear_map(m, streets=None):
    m.clear_layers()
    add_basemap(m,ipyleaflet.basemaps.Esri.WorldImagery)
    return

# Add layer from clicked point in sample TS figure
def click_event(target, m, current_band, df, sample_col, stretch_min, stretch_max, b1, b2, b3):

    pt_index = target['data']['index']
    image_id = df['id'].values[pt_index]
    selected_image = ee.Image(sample_col.filterMetadata('system:index', 'equals', image_id).first())
    tile_url = utils.GetTileLayerUrl(selected_image.visualize(min=stretch_min,
                                                              max=stretch_max,
                                                              bands= [b1, b2, b3]))
    m.add_layer(ipyleaflet.TileLayer(url=tile_url, name=image_id))
