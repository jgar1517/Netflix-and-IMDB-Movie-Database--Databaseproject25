SELECT n.title, n.averageRating, n.release_year
FROM Netflix_IMDB AS n
WHERE n.averageRating IS NOT NULL
GROUP BY n.release_year;
