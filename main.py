import sqlite3
import json
import flask

app = flask.Flask(__name__)


def get_value_from_db(sql):
    print(sql)
    with sqlite3.connect("netflix.db") as connect:
        connect.row_factory = sqlite3.Row
        result = connect.execute(sql).fetchall()

    return result

def search_by_title(title):
    for i in get_value_from_db(sql=f"""
    SELECT *
    from netflix
    where title = '{title}'
    AND release_year = 
    (SELECT max(release_year) as max_value
    from netflix n
    where title = '{title}')
    """):
        return dict(i)


@app.get("/movie/<title>/")
def search_title_view(title):
    response = search_by_title(title=title)
    a = {}
    for key in response.keys():
        if key in ["title","country","release_year"]:
            a[key] = response[key]

    return app.response_class(response=json.dumps(a),
                              status=200,
                              mimetype='application/json')


@app.get("/movie/<year1>/to/<year2>/")
def search_date_view(year1, year2):
    response = get_value_from_db(
        sql=f'''
        SELECT title, release_year
        FROM netflix
        WHERE release_year BETWEEN "{year1}" and "{year2}"
        LIMIT 100
        ''')
    a = []
    for i in response:
        a.append(dict(i))
    return app.response_class(response=json.dumps(a),
                              status=200,
                              mimetype='application/json')

@app.get("/rating/<rating>/")
def search_rating_view(rating):
    rating_dict = {
        "children": ["G"],
        "family": ["G", "PG", "PG-13"],
        "adult": ["R", "NC-17"]
    }
    response = {}
    if rating in rating_dict:
        if len(rating_dict[rating])==0:
            response = {'description': "Список категорий пуст"}
        elif len(rating_dict[rating])<2:
            response = get_value_from_db(sql=f'''
                    SELECT * 
                    FROM netflix 
                    WHERE rating in ('{rating_dict[rating][0]}')
                    ''')
        else:
            response = get_value_from_db(sql=f'''
                    SELECT * 
                    FROM netflix 
                    WHERE rating in {tuple(rating_dict[rating])}
                    ''')

    a = []
    for i in response:
        a.append(dict(i))
    return app.response_class(response=json.dumps(a),
                              status=200,
                              mimetype='application/json')


@app.get("/genre/<genre>/")
def search_genre_view(genre):
    response = get_value_from_db(f'''
                SELECT * 
                FROM netflix n
                WHERE listed_in LIKE "%{genre}%"
                ORDER by release_year
                LIMIT 10''')
    a = []
    for i in response:
        a.append(dict(i))
    return app.response_class(response=json.dumps(a),
                              status=200,
                              mimetype='application/json')

def step_5(name1, name2):
    response = get_value_from_db(
        f'''
            SELECT *
            from netflix n
            WHERE "cast" LIKE "%{name1}%" and "cast" LIKE "%{name2}%"
        '''
    )

    names = []
    result = []
    for i in response:
        c = dict(i).get('cast').split(', ')
        for k in c:
            names.append(k)

    b = [name1,name2]
    names = set(names)-set(b)

    for name in names:
        k = 0
        for i in response:
            if name in dict(i).get('cast'):
                k+=1

        if k>2:
            result.append(name)

    return result

def step_6(type_film, year, genre):
    response = get_value_from_db(sql=f'''
    SELECT * 
    from netflix n
    where "type" = "{type_film}"
    and release_year = "{year}"
    and listed_in LIKE "%{genre}%"
    ''')
    a = []
    for i in response:
        a.append(dict(i))
    return json.dumps(a, indent=4)

if __name__== '__main__':
    print(step_6('TV Show', '2020', 'TV'))
    


