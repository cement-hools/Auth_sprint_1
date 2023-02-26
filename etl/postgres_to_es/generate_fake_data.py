import logging
import random

from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk
from faker import Faker
from load_data import (
    es_create_genre_index,
    es_create_person_index,
    es_create_show_index,
)
from ps_to_es import EsDataclass, EsDataclassGenre, EsDataclassPerson
from settings import settings
from tqdm import tqdm

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

# 400 000 filmworks
# 300 000 actors
# 300 000 writers
# 300 000 directors
NUM_GENRES = 100
NUM_PERSONS = 1000000
NUM_SHOWS = 400000

# Generate genres
fake = Faker(["en_US"])
fake_genre_names = zip(
    fake.words(nb=NUM_GENRES, part_of_speech="adjective", unique=True),
    fake.words(nb=NUM_GENRES, part_of_speech="noun", unique=True),
)
fake_genre_names = [" ".join(g).capitalize() for g in list(fake_genre_names)]
fake_genres = []
for fg in fake_genre_names:
    id = fake.uuid4()
    fake_genres.append(EsDataclassGenre(id=id, underscore_id=id, name=fg))

# Generate persons
fake = Faker(["en_US", "ru_RU"])
fake_persons = []
for _ in tqdm(range(NUM_PERSONS), desc="Generating persons"):
    id = fake.uuid4()
    fake_persons.append(
        EsDataclassPerson(id=id, underscore_id=id, full_name=fake.name())
    )


# Generate Shows
def generate_fake_show(fake_persons, fake_genres):
    for _ in range(NUM_SHOWS):
        id = fake.uuid4()
        directors = random.sample(fake_persons, random.randint(1, 2))
        actors = random.sample(fake_persons, random.randint(0, 7))
        writers = random.sample(fake_persons, random.randint(1, 4))
        yield EsDataclass(
            id=id,
            underscore_id=id,
            imdb_rating=round(random.uniform(1, 10), 2),
            genres=random.sample(fake_genres, random.randint(1, 5)),
            title=fake.text(max_nb_chars=30)[:-1],
            description=fake.text(max_nb_chars=200),
            director=[p.full_name for p in directors],
            actors_names=[p.full_name for p in actors],
            writers_names=[p.full_name for p in writers],
            actors=actors,
            writers=writers,
        ).dict(by_alias=True)


def generate_fake_genre(fake_genres):
    for fg in fake_genres:
        yield fg.dict(by_alias=True)


def generate_fake_person(fake_persons):
    for fp in fake_persons:
        yield fp.dict(by_alias=True)


def push_fake_data_to_elastic(es_client, index, action, total_number):
    progress = tqdm(
        unit="docs", desc=f"Pushing data to {index}", total=total_number
    )
    successes = 0

    for ok, action in streaming_bulk(
        client=es_client,
        index=index,
        actions=action,
        max_retries=100,
        initial_backoff=0.1,
        max_backoff=10,
    ):
        progress.update(1)
        if not ok:
            logger.error(f"Error while streaming fake data to {index}")
        successes += ok
        logger.debug(action)


es_client = Elasticsearch(hosts=settings.elastic_dsn)
es_create_genre_index(es_client)
es_create_person_index(es_client)
es_create_show_index(es_client)

push_fake_data_to_elastic(
    es_client,
    settings.genre_index_name,
    generate_fake_genre(fake_genres),
    NUM_GENRES,
)
push_fake_data_to_elastic(
    es_client,
    settings.person_index_name,
    generate_fake_person(fake_persons),
    NUM_PERSONS,
)
push_fake_data_to_elastic(
    es_client,
    settings.show_index_name,
    generate_fake_show(fake_persons, fake_genres),
    NUM_SHOWS,
)
