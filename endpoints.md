## 1. Главная страница

### Запрос
```
GET /api/v1/films?sort=-imdb_rating&page[size]=50&page[number]=1
```

### Формат ответа
```
[
    {
        "uuid": "uuid",
        "title": "str",
        "imdb_rating": "float"
    },
]
```
### Пример ответа
```
[
    {
        "uuid": "524e4331-e14b-24d3-a156-426614174003",
        "title": "Ringo Rocket Star and His Song for Yuri Gagarin",
        "imdb_rating": 9.4
    },
    {
        "uuid": "524e4331-e14b-24d3-a156-426614174003",
        "title": "Lunar: The Silver Star",
        "imdb_rating": 9.2
    },
...
]
```
## 2. Жанр и популярные фильмы в нём. Это просто фильтрация

### Запрос
```
GET /api/v1/films?filter[genre]=<uuid:UUID>&sort=-imdb_rating&page[size]=50&page[number]=1
```

### Формат ответа
```
[
    {
        "uuid": "uuid",
        "title": "str",
        "imdb_rating": "float"
    },
...
]
```
### Пример ответа
```
[
    {
        "uuid": "524e4331-e14b-24d3-a156-426614174003",
        "title": "Ringo Rocket Star and His Song for Yuri Gagarin",
        "imdb_rating": 9.4
    },
    {
        "uuid": "524e4331-e14b-24d3-a156-426614174003",
        "title": "Lunar: The Silver Star",
        "imdb_rating": 9.2
    },
...
] 
```

## 3. Главная страница

### Запрос
```

```

### Формат ответа
```

```
### Пример ответа
```

```


## 3. Главная страница

### Запрос
```

```

### Формат ответа
```

```
### Пример ответа
```

```