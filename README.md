# Notion Flix Enhance

Notion Flix Enhance is a Python program designed to enhance your media database stored in Notion by retrieving detailed information about movies and TV shows using the TMDB API. It allows you to gather essential details like directors, producers, runtime (in hours), and episode count for TV shows. This information is then added to your Notion database, along with links to watch the media and YouTube trailers.

## Table of Contents

-   [Introduction](#notion-flix-enhance)
-   [Table of Contents](#table-of-contents)
-   [Features](#features)
-   [Getting Started](#getting-started)
    -   [Prerequisites](#prerequisites)
    -   [Installation](#installation)
    -   [Configuration](#configuration)
-   [Usage](#usage)
-   [Project Structure](#project-structure)
-   [Contributing](#contributing)
-   [License](#license)

## Features

-   Retrieve media details (directors, producers, runtime, episode count) using the TMDB API.
-   Seamlessly integrate with your Notion database to update media records.
-   Store links to where to watch the media and YouTube trailers.
-   Customizable and extendable codebase.
-   Type hinting for improved code readability.

## Getting Started

### Prerequisites

Before you begin, ensure you have the following prerequisites:

-   Python 3.6 or higher installed on your machine.
-   TMDB API key and Notion API key.
-   Notion database ID where you want to store the media information.

### Installation

1. Clone the repository:

```bash
git clone https://github.com/tabdhsan/notion-flix-enhance.git
cd notion-flix-enhance
```

### Configuration

1. Rename the .env.example file to .env and provide your TMDB API key, Notion API key and Notion Datebase ID.

```bash
TMDB_API_KEY=your_tmdb_api_key
NOTION_API_KEY=your_notion_api_key
NOTION_DATABASE_ID=your_notion_database_id
```

2. Modify the config.py file to adjust any configuration parameters according to your needs.

### Usage

1. Run the main program to enhance your media database:

```bash
python notion_flix_enhance.py
```

2. The program will gather media details using TMDB API and update your Notion database accordingly.

### Project Structure

The project is organized as follows:

-   tmdb_crud_and_cleanup.py: Handles TMDB API calls and data cleaning.
-   notion_crud_and_cleanup.py: Manages Notion API interactions and data manipulation.
-   notion_tmdb_wrappers.py: Contains wrapper functions combining TMDB and Notion functionalities.
-   notion_flix_enhance.py: Main program to run the enhancement process.
-   config.py: Configuration settings.
-   custom_types.py: Custom Python types for type hinting.

### Contributing

Contributions are welcome! Please feel free to open issues or submit pull requests for any improvements or bug fixes.

### License

Distributed under the MIT License

### Happy coding 🥳

Enhance your Notion media database with detailed information using the power of TMDB API. Keep track of directors, producers, runtime, and episode counts effortlessly.
