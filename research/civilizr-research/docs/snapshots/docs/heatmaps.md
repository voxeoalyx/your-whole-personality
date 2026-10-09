You can use the Insights API to create interactive heatmaps that visually depict the concentration or dispersion of signal for an entity across various geographical locations. Heatmaps offer an intuitive way to explore and understand the geographic distribution of signals, uncovering insights and patterns in consumer preferences across different areas.

# Key Features and Benefits

Qloo's heatmaps give you deep insight into geolocational data:

- **Visualize Entity Presence**: Access a visual representation of the signal for a specific entity in a given area. This enables you to identify areas with a strong presence or preference for the entity.
- **Identify Hotspots and Trends**: Easily identify hotspots where the entity's affinity score is highly concentrated and discover emerging trends or patterns across different geographical locations.
- **Make Informed Decisions**: Use heatmap data to inform decisions about marketing strategies, location-based targeting, and understanding user preferences in specific areas.

# How It Works

Heatmaps create a visual representation of a few key metrics. These metrics include an entity's affinity and popularity within specific geohashes. By leveraging these pre-calculated scores, the heatmap offers valuable insights into an entity's relative strength and popularity in various geographic areas. This enables you to visualize the concentration or dispersion of interest for the entity across different locations.

Each point in the heatmap is assigned three scores, providing a comprehensive understanding of the entity's presence within the selected location:

- **Affinity Rank Score:** This measures how well an entity (like a brand or product) performs compared to itself in the area of interest.
- **Popularity Score:** This percentile score reflects the entity's popularity within the geohash, indicating its signal density within a specific area by comparing it to other entities in the same location.
- **Affinity in Geospatial Context:** This compares an entity to other entities within a geographic location, both locally and globally. The affinity score provides a normalized measure of how much interest people in a specific location have in an entity, compared to other entities with signals in that area. This helps assess the relative level of interest across different locations from both a local and broader perspective.

## Interpretation

By combining these scores, the heatmap uses warmer colors to indicate higher concentrations of signal, while cooler colors represent lower concentrations, signifying a more dispersed or less significant presence of the entity.
