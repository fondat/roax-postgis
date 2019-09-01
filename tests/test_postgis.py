import pytest
import roax.db as db
import roax.geo as geo
import roax.postgis as postgis
import roax.postgresql as postgresql
import roax.schema as s
import uuid


_schema = s.dict(
    {
        "id": s.uuid(),
        "point": geo.Point(),
        "linestring": geo.LineString(),
        "polygon": geo.Polygon(),
        "multipoint": geo.MultiPoint(),
        "multilinestring": geo.MultiLineString(),
        "multipolygon": geo.MultiPolygon(),
        "geometrycollection": geo.GeometryCollection(),
    }
)


_point = {"type": "Point", "coordinates": [100.0, 0.0]}

_linestring = {"type": "LineString", "coordinates": [[100.0, 0.0], [101.0, 1.0]]}

_polygon_holes = {
    "type": "Polygon",
    "coordinates": [
        [[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]],
        [[100.8, 0.8], [100.8, 0.2], [100.2, 0.2], [100.2, 0.8], [100.8, 0.8]],
    ],
}

_multipoint = {"type": "MultiPoint", "coordinates": [[100.0, 0.0], [101.0, 1.0]]}

_multilinestring = {
    "type": "MultiLineString",
    "coordinates": [[[100.0, 0.0], [101.0, 1.0]], [[102.0, 2.0], [103.0, 3.0]]],
}

_multipolygon = {
    "type": "MultiPolygon",
    "coordinates": [
        [[[102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0]]],
        [
            [[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]],
            [[100.2, 0.2], [100.2, 0.8], [100.8, 0.8], [100.8, 0.2], [100.2, 0.2]],
        ],
    ],
}

_geometrycollection = {
    "type": "GeometryCollection",
    "geometries": [
        {"type": "Point", "coordinates": [100.0, 0.0]},
        {"type": "LineString", "coordinates": [[101.0, 0.0], [102.0, 1.0]]},
    ],
}


@pytest.fixture(scope="module")
def database():
    db = postgresql.Database(minconn=1, maxconn=10, dbname="roax_postgis")
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
    return db.Table(database, "foo", _schema, "id", postgis.adapters)


@pytest.fixture()
def resource(database, table):
    return db.TableResource(table)


def test_crud(resource):
    id = uuid.uuid4()
    body = {
        "id": id,
        "point": _point,
        "linestring": _linestring,
        "polygon": _polygon_holes,
        "multipoint": _multipoint,
        "multilinestring": _multilinestring,
        "multipolygon": _multipolygon,
        "geometrycollection": _geometrycollection,
    }
    resource.create(id, body)
    assert resource.read(id) == body
