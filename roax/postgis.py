"""Module to manage resource items in a PostgreSQL database with PostGIS extensions."""

import roax.geo as geo
import roax.schema


_bytes = roax.schema.bytes(format="hex")


class _GeometryAdapter:
    def encode(self, schema, value):
        return _bytes.str_encode(schema.bin_encode(value))  # WKB hex string

    def decode(self, schema, value):
        return schema.bin_decode(_bytes.str_decode(value))  # WKB hex string


_geometry = _GeometryAdapter()


adapters = {
    geo.Point: _geometry,
    geo.LineString: _geometry,
    geo.Polygon: _geometry,
    geo.MultiPoint: _geometry,
    geo.MultiLineString: _geometry,
    geo.MultiPolygon: _geometry,
    geo.GeometryCollection: _geometry,
}
