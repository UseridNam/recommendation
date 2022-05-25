
from fastapi import FastAPI, Path, Query, HTTPException, status
import pandas as pd
from typing import Optional
import requests

app = FastAPI()

api_key = '15d2ea6d0dc1d476efbca3eba2b9bbfb'
recommendation_payload = {'api_key': api_key, 'language': 'en-US'}
r = requests.get('https://api.themoviedb.org/3/genre/movie/list',
                            params=recommendation_payload, timeout=10).json()['genres']
movie_genres=dict()
for genre in r:
    movie_genres[str(genre['id'])]=genre['name']
@app.get("/recommendation/{title}")
async def recommendation(title: str = Path(None, description="Title of the basis movie (mandatory)"),
                         #limit: Optional[int] = Query(None, description="Max nr of movies to list."),
                         #genre: Optional[str] = Query(None, description="Search by genre"),
                         #director: Optional[str] = Query(None, description="Search by director"),
                         #actor: Optional[str] = Query(None, description="Search by actor"),
                         #keyword: Optional[str] = Query(None, description="Search by a keyword from description"),
                         #release_year: Optional[int] = Query(None, description="Search by release year")
                         ):

    movie_payload = {
        'api_key': api_key,
        'language': 'en-US',
        'include_adult': 'false',
        'query': title
    }

    r = requests.get('https://api.themoviedb.org/3/search/movie',
                     params=movie_payload, timeout=10)

    if(not r.ok):
        raise HTTPException(status_code=r.status_code, detail="Some error")

    if(r.json()['total_results'] == 0):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No movie found")

    movie_id = r.json()['results'][0]['id']

    r = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}/recommendations', params=recommendation_payload, timeout=10)

    if(not r.ok):
        raise HTTPException(status_code=r.status_code, detail="Some error")
    
    results = r.json()['results']
    for movie in results:
        movie['poster_path'] = 'https://image.tmdb.org/t/p/original' + movie['poster_path']

        imdb_id = requests.get(
            f'https://api.themoviedb.org/3/movie/{movie_id}',
            params=recommendation_payload,
            timeout=10).json()['imdb_id']
        movie['imdb_path'] = 'https://www.imdb.com/title/' + imdb_id

        providers = requests.get(
            f'https://api.themoviedb.org/3/movie/{movie_id}/watch/providers?api_key={api_key}',
            timeout=10).json()['results']['FI']

        if 'flatrate' in providers:
            movie['providers'] = providers['flatrate']
        else:
            movie['providers'] = providers['buy']

        for provider in movie['providers']:
            provider['logo_path'] = 'https://image.tmdb.org/t/p/original' + provider['logo_path']

        genres=[]
        for genre in movie['genre_ids']:
           genres.append(movie_genres[str(genre)])
        movie['genre_ids']=genres
        movie['release_date']=movie['release_date'][0:4]
    return results

#for TV series.

tv_r = requests.get('https://api.themoviedb.org/3/genre/tv/list',
                            params=recommendation_payload, timeout=10).json()['genres']
TV_genres=dict()
for genre in tv_r:
    TV_genres[str(genre['id'])]=genre['name']
@app.get("/recommendation/{title}")
async def recommendation(title: str = Path(None, description="Title of the basis TV serie (mandatory)"),
                         #limit: Optional[int] = Query(None, description="Max nr of movies to list."),
                         #genre: Optional[str] = Query(None, description="Search by genre"),
                         #director: Optional[str] = Query(None, description="Search by director"),
                         #actor: Optional[str] = Query(None, description="Search by actor"),
                         #keyword: Optional[str] = Query(None, description="Search by a keyword from description"),
                         #release_year: Optional[int] = Query(None, description="Search by release year")
                         ):

    TV_payload = {
        'api_key': api_key,
        'language': 'en-US',
        'include_adult': 'false',
        'query': title
    }

    r = requests.get('https://api.themoviedb.org/3/search/tv',
                     params=TV_payload, timeout=10)

    if(not tv_r.ok):
        raise HTTPException(status_code=tv_r.status_code, detail="Some error")

    if(tv_r.json()['total_results'] == 0):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No movie found")

    tv_id = tv_r.json()['results'][0]['id']

    tv_r = requests.get(f'https://api.themoviedb.org/3/tv/{tv_id}/recommendations', params=recommendation_payload, timeout=10)

    if(not tv_r.ok):
        raise HTTPException(status_code=tv_r.status_code, detail="Some error")
    
    results = tv_r.json()['results']
    for tv_serie in results:
        tv_serie['poster_path'] = 'https://image.tmdb.org/t/p/original' + tv_serie['poster_path']

        imdb_id = requests.get(
            f'https://api.themoviedb.org/3/tv/{tv_id}',
            params=recommendation_payload,
            timeout=10).json()['imdb_id']
        tv_serie['imdb_path'] = 'https://www.imdb.com/title/' + imdb_id

        providers = requests.get(
            f'https://api.themoviedb.org/3/movie/{tv_id}/watch/providers?api_key={api_key}',
            timeout=10).json()['results']['FI']

        if 'flatrate' in providers:
            tv_serie['providers'] = providers['flatrate']
        else:
            tv_serie['providers'] = providers['buy']

        for provider in tv_serie['providers']:
            provider['logo_path'] = 'https://image.tmdb.org/t/p/original' + provider['logo_path']

        genres=[]
        for genre in tv_serie['genre_ids']:
           genres.append(TV_genres[str(genre)])
        tv_serie['genre_ids']=genres
        tv_serie['release_date']=tv_serie['release_date'][0:4]
    return results
