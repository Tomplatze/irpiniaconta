"""Source-preserving geographic evidence for collection, not product indicators."""
from __future__ import annotations

import io
import json
from pathlib import Path
from zipfile import ZipFile

from pyproj import CRS, Transformer
import shapefile
from shapely.geometry import shape, mapping
from shapely.ops import transform


def official_boundaries(path: Path, job: dict[str, object], geo, sink) -> dict[str, object]:
    """Transform official geometries to WGS84 using their actual PRJ definition."""
    with ZipFile(path) as archive:
        base = str(job['member_base'])
        crs = CRS.from_wkt(archive.read(base + '.prj').decode())
        transformer = Transformer.from_crs(crs, 'EPSG:4326', always_xy=True)
        reader = shapefile.Reader(shp=io.BytesIO(archive.read(base + '.shp')),
                                  shx=io.BytesIO(archive.read(base + '.shx')),
                                  dbf=io.BytesIO(archive.read(base + '.dbf')), encoding='utf-8')
        points = []
        features = []
        invalid = []
        for record in reader.iterShapeRecords():
            properties = record.record.as_dict()
            codes = geo.resolve(properties, {'key_rule': 'istat', 'key_column': 'PRO_COM_T'})
            if not codes:
                continue
            geometry = transform(transformer.transform, shape(record.shape.__geo_interface__))
            if not geometry.is_valid:
                invalid.append(codes[0])
            point = geometry.representative_point()
            points.append({'municipality_code': codes[0], 'longitude': round(point.x, 6), 'latitude': round(point.y, 6),
                           'method': 'Interior representative point of ISTAT 2026 municipal geometry; not a town centre'})
            feature = {'type': 'Feature', 'properties': {'municipality_code': codes[0], **properties}, 'geometry': mapping(geometry)}
            features.append(feature)
            sink.add('municipal_boundaries', {'properties': properties, 'geometry': mapping(geometry), 'source_crs': crs.to_string()}, codes, '2026-01-01')
    if len(features) != 118 or {item['properties']['municipality_code'] for item in features} != geo.codes:
        raise ValueError('Official boundary coverage does not match the 118 current municipalities')
    output = sink.output.parent
    (output / 'municipal-boundaries.geojson').write_text(json.dumps({'type': 'FeatureCollection', 'features': features}) + '\n')
    (output / 'municipal-weather-points.json').write_text(json.dumps(sorted(points, key=lambda item: item['municipality_code']), indent=2) + '\n')
    return {'source_crs': crs.to_string(), 'output_crs': 'EPSG:4326', 'invalid_source_geometry_codes': invalid,
            'derived_points_method': 'Interior representative point, not official town-centre coordinates'}


def geojson(path: Path, job: dict[str, object], geo, sink) -> dict[str, object]:
    """Associate source features spatially, without claiming exhaustive inventories."""
    data = json.loads(path.read_text())
    if data.get('type') != 'FeatureCollection' or (data.get('exceededTransferLimit') and not job.get('paginated_total_count')):
        raise ValueError('Expected complete GeoJSON FeatureCollection')
    if job.get('expected_count') is not None and len(data['features']) != job['expected_count']:
        raise ValueError('GeoJSON count differs from the independent source count')
    identifiers = [feature.get('id', feature.get('properties', {}).get('OBJECTID')) for feature in data['features']]
    if job.get('paginated_total_count') and (None in identifiers or len(set(identifiers)) != len(identifiers)):
        raise ValueError('Paginated GeoJSON requires unique source feature identifiers')
    boundaries = json.loads((sink.output.parent / 'municipal-boundaries.geojson').read_text())['features']
    areas = [(item['properties']['municipality_code'], shape(item['geometry'])) for item in boundaries]
    for index, feature in enumerate(data['features']):
        geometry = shape(feature['geometry']) if feature.get('geometry') else None
        codes = sorted(code for code, area in areas if geometry is not None and area.intersects(geometry))
        sink.add('features', {'source_feature_index': index, **feature}, codes, str(job.get('period', 'undated')))
    return {'association_method': 'Geometric intersection with ISTAT 2026 boundaries; multiple municipalities preserved',
            'source_feature_count': len(data['features']),
            'source_feature_ids': identifiers if job.get('paginated_total_count') else None}


def spatial_areas(output: Path):
    """Read the staged authoritative geographic frame for local association."""
    data = json.loads((output / 'municipal-boundaries.geojson').read_text())
    return [(item['properties']['municipality_code'], shape(item['geometry'])) for item in data['features']]


def natura(path: Path, job: dict[str, object], geo, sink) -> dict[str, object]:
    """Clip Natura 2000 associations using the publisher CRS and original sites."""
    areas = spatial_areas(sink.output.parent)
    invalid = []
    with ZipFile(path) as archive:
        base = next(name[:-4] for name in archive.namelist() if name.endswith('.shp'))
        crs = CRS.from_wkt(archive.read(base + '.prj').decode())
        encoding = archive.read(base + '.cpg').decode().strip()
        transformer = Transformer.from_crs(crs, 'EPSG:4326', always_xy=True)
        reader = shapefile.Reader(shp=io.BytesIO(archive.read(base + '.shp')),
                                  dbf=io.BytesIO(archive.read(base + '.dbf')), encoding=encoding)
        for record in reader.iterShapeRecords():
            properties = record.record.as_dict()
            if properties['regione'] != 'Campania':
                continue
            geometry = transform(transformer.transform, shape(record.shape.__geo_interface__))
            if not geometry.is_valid:
                invalid.append(properties['site_code'])
                from shapely import make_valid
                intersection_geometry = make_valid(geometry)
            else:
                intersection_geometry = geometry
            codes = [code for code, area in areas if intersection_geometry.intersects(area)]
            sink.add('natura2000_sites', {'properties': properties, 'geometry': mapping(geometry),
                                         'source_geometry_valid': geometry.is_valid}, sorted(codes), '2025-12')
    return {'source_crs': crs.to_string(), 'association_method': 'Site geometry intersects ISTAT 2026 municipality; original site geometry retained',
            'invalid_source_site_codes': invalid, 'notes': 'Overlapping protection designations are not additive; this is Natura 2000, not all protected areas.'}


def osm(path: Path, job: dict[str, object], geo, sink) -> dict[str, object]:
    """Retain crowdsourced infrastructure with source IDs and spatial associations."""
    data = json.loads(path.read_text())
    if data.get('remark') or 'elements' not in data:
        raise ValueError('Overpass returned an error or incomplete query')
    areas = spatial_areas(sink.output.parent)
    timestamp = data['osm3s']['timestamp_osm_base']
    for item in data['elements']:
        if item['type'] == 'node':
            geometry = shape({'type': 'Point', 'coordinates': [item['lon'], item['lat']]})
        elif item['type'] == 'way' and len(item.get('geometry', [])) >= 2:
            geometry = shape({'type': 'LineString', 'coordinates': [[point['lon'], point['lat']] for point in item['geometry']]})
        else:
            continue
        codes = [code for code, area in areas if area.intersects(geometry)]
        sink.add('mapped_infrastructure', {'osm': item, 'geometry': mapping(geometry)}, sorted(codes), timestamp[:10])
    return {'osm_base_timestamp': timestamp, 'notes': 'Mapped rails, stations and stops; no schedules, operating status or exhaustive municipal inventory inferred.'}


def events(path: Path, job: dict[str, object], geo, sink) -> dict[str, object]:
    """Associate recorded earthquake epicentres; do not infer municipal hazard."""
    import csv
    areas = spatial_areas(sink.output.parent)
    with path.open(encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle, delimiter='|')
        if reader.fieldnames is None or not {'#EventID', 'Latitude', 'Longitude', 'Time'}.issubset(reader.fieldnames):
            raise ValueError('INGV FDSN text schema changed')
        for item in reader:
            geometry = shape({'type': 'Point', 'coordinates': [float(item['Longitude']), float(item['Latitude'])]})
            codes = [code for code, area in areas if area.intersects(geometry)]
            sink.add('earthquake_epicentres', item, sorted(codes), item['Time'][:4])
    return {'notes': 'Recorded epicentres inside current municipal boundaries. Magnitude/location uncertainty and catalog completeness retained; no hazard ranking derived.'}


def esri_lines(path: Path, job: dict[str, object], geo, sink) -> dict[str, object]:
    """Retain complete Esri line features when their GeoJSON export fails."""
    data = json.loads(path.read_text())
    if data.get('error') or data.get('geometryType') != 'esriGeometryPolyline' or data.get('exceededTransferLimit'):
        raise ValueError('Expected complete Esri polyline response')
    if data.get('spatialReference', {}).get('latestWkid', data.get('spatialReference', {}).get('wkid')) != 4326:
        raise ValueError('Esri line response is not WGS84')
    if len(data['features']) != job['expected_count']:
        raise ValueError('Esri line count differs from independent source count')
    areas = spatial_areas(sink.output.parent)
    for feature in data['features']:
        paths = feature['geometry']['paths']
        geometry = shape({'type': 'MultiLineString', 'coordinates': [[[point[0], point[1]] for point in path] for path in paths]})
        codes = [code for code, area in areas if area.intersects(geometry)]
        sink.add('line_features', {'esri_feature': feature, 'geometry': mapping(geometry)}, sorted(codes), 'undated_publisher_layer')
    return {'source_feature_count': len(data['features']), 'association_method': 'Esri WGS84 line intersection with official 2026 municipal geometry',
            'notes': 'Original Esri feature retained. Historic project/classification fields are not evidence of current operations.'}


def weather(path: Path, job: dict[str, object], geo, sink) -> dict[str, object]:
    """Retain daily reanalysis and actual returned grid coordinates per request."""
    from datetime import date, timedelta
    data = json.loads(path.read_text())
    series = data if isinstance(data, list) else [data]
    requests = job['locations']
    if len(series) != len(requests) or any(request['municipality_code'] not in geo.codes for request in requests):
        raise ValueError('Weather response/request location mismatch')
    start, end = date.fromisoformat(str(job['start_date'])), date.fromisoformat(str(job['end_date']))
    expected_dates = [(start + timedelta(days=index)).isoformat() for index in range((end - start).days + 1)]
    grids = []
    for response, request in zip(series, requests):
        if response.get('error') or response.get('daily', {}).get('time') != expected_dates:
            raise ValueError('Weather response has an error or incomplete/reordered daily dates')
        daily = response['daily']
        fields = {key: values for key, values in daily.items() if key != 'time'}
        if any(len(values) != len(expected_dates) for values in fields.values()):
            raise ValueError('Weather variable shape mismatch')
        grid = {'latitude': response['latitude'], 'longitude': response['longitude'], 'elevation': response['elevation'],
                'timezone': response['timezone'], 'daily_units': response['daily_units'], 'request': request}
        grids.append(grid)
        for index, day in enumerate(expected_dates):
            sink.add('daily_reanalysis', {'date': day, **{key: values[index] for key, values in fields.items()},
                                          'grid': grid, 'model': job['model']}, [request['municipality_code']], day[:4])
    return {'geography_semantics': 'Reanalysis at one interior representative point per municipality, not municipal averages or station observations',
            'model': job['model'], 'returned_grids': grids, 'date_range': [start.isoformat(), end.isoformat()]}
