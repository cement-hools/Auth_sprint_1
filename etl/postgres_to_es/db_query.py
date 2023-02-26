create_a_table = """
create table if not exists states
(
    load_time  TIMESTAMP
            constraint id
            primary key
                on conflict fail,
    successful BOOL      default FALSE             not null,
    created_at TIMESTAMP default CURRENT_TIMESTAMP not null

);
"""

delete_old_states = """
delete
from states
where created_at < DATETIME('now', '-1 year')
"""

last_success_load_time = """
select load_time
from states
where successful = TRUE
order by created_at DESC
limit 1
"""

insert_last_successful_load_time = """
INSERT OR
REPLACE INTO states (load_time, successful, created_at)
VALUES ('{0}', {1}, '{2}');
"""

load_person_q = "SELECT id, full_name FROM content.person GROUP BY id"

load_person_role = """SELECT p.id, p.full_name, p.birth_date, 
                      ARRAY_AGG(DISTINCT pfw.role) AS role,       
                      ARRAY_AGG(DISTINCT pfw.film_work_id) AS film_ids
                      FROM content.person as p LEFT JOIN content.person_film_work as pfw 
                      ON p.id = pfw.person_id GROUP BY p.id"""

load_film_id = """SELECT id FROM content.film_work LIMIT 1"""

big_request = """ARRAY_AGG(DISTINCT jsonb_build_object('name', g.name, 'id', g.id)) AS genre,
                 ARRAY_AGG(DISTINCT jsonb_build_object('id', p.id, 'name', p.full_name)) 
                 FILTER (WHERE pfw.role = 'director') AS director,
                 ARRAY_AGG(DISTINCT jsonb_build_object('id', p.id, 'name', p.full_name)) 
                 FILTER (WHERE pfw.role = 'actor') AS actors,
                 ARRAY_AGG(DISTINCT jsonb_build_object('id', p.id, 'name', p.full_name)) 
                 FILTER (WHERE pfw.role = 'writer') AS writers,
                 ARRAY_AGG(DISTINCT p.full_name) FILTER (WHERE pfw.role = 'actor') AS actors_names,
                 ARRAY_AGG(DISTINCT p.full_name) FILTER (WHERE pfw.role = 'writer') AS writers_names"""

full_load = """
select fw.id                                           AS                id,
       fw.title                                        AS                title,
       fw.description                                  AS                description,
       fw.rating                                       AS                imdb_rating,
       ARRAY_AGG(DISTINCT g.id || ':::' || g.name)     AS                genres,
       ARRAY_AGG(DISTINCT p.id || ':::' || pfw.role || ':::' || p.full_name) persons
from content.film_work fw
         left join content.person_film_work pfw on fw.id = pfw.film_work_id
         left join content.person p on pfw.person_id = p.id
         left join content.genre_film_work gfw on fw.id = gfw.film_work_id
         left join content.genre g on gfw.genre_id = g.id
group by fw.id
having MAX(fw.modified) > '{0}'
    OR MAX(p.modified) > '{0}'
    OR MAX(g.modified) > '{0}';
        """

query_all_genre = """SELECT id, name, description
                 FROM content.genre
                 ORDER BY created;"""
