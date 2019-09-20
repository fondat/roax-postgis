import dataclasses
import geojson
import pytest
import roax.db
import roax.geo
import roax.postgis
import roax.postgresql
import roax.schema as s
import uuid


@dataclasses.dataclass
class DC:
    id: s.uuid()
    point: roax.geo.Point()
    linestring: roax.geo.LineString()
    polygon: roax.geo.Polygon()
    multipoint: roax.geo.MultiPoint()
    multilinestring: roax.geo.MultiLineString()
    multipolygon: roax.geo.MultiPolygon()
    geometrycollection: roax.geo.GeometryCollection()


_schema = s.dataclass(DC)


_point = geojson.Point([100.0, 0.0])

_linestring = geojson.LineString([[100.0, 0.0], [101.0, 1.0]])

_polygon_holes = geojson.Polygon(
    [
        [[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]],
        [[100.8, 0.8], [100.8, 0.2], [100.2, 0.2], [100.2, 0.8], [100.8, 0.8]],
    ]
)

_multipoint = geojson.MultiPoint([[100.0, 0.0], [101.0, 1.0]])

_multilinestring = geojson.MultiLineString(
    [[[100.0, 0.0], [101.0, 1.0]], [[102.0, 2.0], [103.0, 3.0]]]
)

_multipolygon = geojson.MultiPolygon(
    [
        [[[102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0]]],
        [
            [[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]],
            [[100.2, 0.2], [100.2, 0.8], [100.8, 0.8], [100.8, 0.2], [100.2, 0.2]],
        ],
    ]
)

_geometrycollection = geojson.GeometryCollection(
    geometries=[
        geojson.Point([100.0, 0.0]),
        geojson.LineString([[101.0, 0.0], [102.0, 1.0]]),
    ]
)


@pytest.fixture(scope="module")
def database():
    db = roax.postgresql.Database(minconn=1, maxconn=10, dbname="roax_postgis")
    with db.cursor() as cursor:
        cursor.execute(
            """
                CREATE TABLE FOO (
                    id TEXT,
                    point GEOGRAPHY,
                    linestring GEOGRAPHY,
                    polygon GEOGRAPHY,
                    multipoint GEOGRAPHY,
                    multilinestring GEOGRAPHY,
                    multipolygon GEOGRAPHY,
                    geometrycollection GEOGRAPHY
                );
            """
        )
    yield db
    with db.cursor() as cursor:
        cursor.execute("DROP TABLE FOO;")


@pytest.fixture()
def table(database):
    with database.cursor() as cursor:
        cursor.execute("DELETE FROM FOO;")
    return roax.db.Table(database, "foo", _schema, "id", roax.postgis.adapters)


@pytest.fixture()
def resource(database, table):
    return roax.db.TableResource(table)


def test_crud(resource):
    id = uuid.uuid4()
    body = DC(
        id=id,
        point=_point,
        linestring=_linestring,
        polygon=_polygon_holes,
        multipoint=_multipoint,
        multilinestring=_multilinestring,
        multipolygon=_multipolygon,
        geometrycollection=_geometrycollection,
    )
    resource.create(id, body)
    assert resource.read(id) == body
