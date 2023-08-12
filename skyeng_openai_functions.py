signature_login = {
    "name": "login",
    "description": "Login to Skyeng. Other functions will not work without authorization. The user must provide an email and password before using the rest of the features.",
    "parameters": {
        "type": "object",
        "properties": {
            "username": {"type": "string", "description": "Username for login"},
            "password": {"type": "string", "description": "Password for login"}
        },
        "required": ["username", "password"]
    }
}

signature_get_word_sets = {
    "name": "get_word_sets",
    "description": "Retrieve word sets by page. This is a set of words that go along with the topic of the lesson. Teachers add words to these sets for users, and this function returns data on the user's current sets for the specified page.",
    "parameters": {
        "type": "object",
        "properties": {
            "page_number": {"type": "integer", "description": "Page number to retrieve"},
            "page_size": {"type": "integer", "description": "Number of word sets per page"}
        },
        "required": ["page_number", "page_size"]
    }
}

signature_get_words_from_set = {
    "name": "get_words_from_set",
    "description": "This function returns words data for a specific set (Students also call these 'topics' or 'topics'). Data contains info about words: progress, status, isLearned, createdAt.",
    "parameters": {
        "type": "object",
        "properties": {
            "set_id": {"type": "integer", "description": "ID of the word set"}
        },
        "required": ["set_id"]
    }
}

signature_get_words_data = {
    "name": "get_words_data",
    "description": "Get words data of words. Data that can be retrieved: alternatives, definition, examples, id, images, sound_url, text, transcription, translation. Please, don't provide useless info like ",
    "parameters": {
        "type": "object",
        "properties": {
            "word_ids": {
                "type": "array",
                "description": "List of ids for words. These ids can be found in sets, in word objects.",
                "items": {
                    "type": "string"
                }
            }
        },
        "required": ["word_ids"]
    }
}

all_functions = [signature_login, signature_get_word_sets, signature_get_words_from_set, signature_get_words_data]
