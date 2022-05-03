GET /movies/_search
{
    "query": {
        "bool": {
            "should": [
                {
                    "nested": {
                        "path": "actors",
                        "query": {
                            "term": {
                                "actors.uuid": "8856053e-8a4f-42e1-bb27-6ab8fd664518"
                            }
                        }
                    }
                },
                {
                    "nested": {
                        "path": "writers",
                        "query": {
                            "term": {
                                "writers.uuid": "8856053e-8a4f-42e1-bb27-6ab8fd664518"
                            }
                        }
                    }
                },
                {
                    "nested": {
                        "path": "directors",
                        "query": {
                            "term": {
                                "directors.uuid": "8856053e-8a4f-42e1-bb27-6ab8fd664518"
                            }
                        }
                    }
                }
            ]
        }
    }
}

