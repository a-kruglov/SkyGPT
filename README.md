# SkyGPT

SkyGPT is a language learning platform that integrates with Skyeng, providing interactive chat functionalities using OpenAI's GPT models. The project offers features for teachers and students to interact with lessons, words, and topics.

## Features

- **User Authentication**: Secure login to Skyeng with username and password.
- **Word Sets Management**: Retrieve word sets by page, words from specific sets, and detailed data about specific words.
- **Interactive Chat**: Engage in interactive chat sessions using GPT models, with support for specific function calls related to language learning.
- **Database Integration**: Store and manage user tokens and chat messages using SQLite.

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/a-kruglov/SkyGPT.git
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure the `config.json` file with the necessary parameters, including the OpenAI API key.

## Usage

Run the main script to start the application:
```
python main.py
```

## Files Overview

- `chat_gpt.py`: Manages chat interactions using GPT models.
- `skyeng_database.py`: Handles interactions with SQLite for token management.
- `skyeng_openai_functions.py`: Defines function signatures for chat interactions.
- `skyeng_user.py`: Manages user-related functionalities, including authentication and data retrieval.

## Contributing

Feel free to fork the repository and submit pull requests for enhancements, bug fixes, or new features.

## License

MIT
