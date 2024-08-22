import folium

# Define the polygon coordinates
quan_son_poly=[
    [104.6063, 20.4116],
    [105.1309, 20.4116],
    [105.1309, 20.0953],
    [104.6063, 20.0953],
    [104.6063, 20.4116]
]
# Reverse the coordinates to (latitude, longitude) format
quan_son_poly = [[lat, lon] for lon, lat in quan_son_poly]

# Create a Folium map centered around the polygon
m = folium.Map(location=[19.86565, 105.86305], zoom_start=12)

# Add the polygon to the map
folium.Polygon(locations=quan_son_poly, color='blue', fill=True, fill_color='blue').add_to(m)

# Display the map
m.save('quan_son.html')