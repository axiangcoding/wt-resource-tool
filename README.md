# WT Resource Tool

[![PyPI version](https://img.shields.io/pypi/v/wt-resource-tool.svg)](https://pypi.org/project/wt-resource-tool/)
[![License](https://img.shields.io/github/license/axiangcoding/wt-resource-tool.svg)](https://github.com/axiangcoding/wt-resource-tool/blob/main/LICENSE)

> [!WARNING]
> This project remains under active development, meaning API may be unstable. Use at your own risk.

**wt-resource-tool** (WTRT) is a powerful Python library that reads and parses various data types from the [War-Thunder-Datamine](https://github.com/gszabi99/War-Thunder-Datamine) repository into type-annotated, easy-to-use Python objects.

Everything we do is designed to help you focus more intently on creating awesome projects for the War Thunder community.

## Not Affiliated with Gaijin Entertainment

This project is not affiliated with Gaijin Entertainment or the War Thunder game.

## ✨ Features

- **🚀 Easy to Use**: Install via `pip`, `poetry`, or `uv` and start working immediately
- **📖 Human-Readable**: All data is parsed into clean, type-annotated Python objects with full IDE support
- **🎯 Type-Safe**: Comprehensive type hints for all data structures and APIs
- **⚡ Async Support**: Built with modern async/await patterns for efficient data processing
- **🔧 Flexible Architecture**: Choose between direct parsing for custom implementations or memory-based storage for quick queries
- **🌐 Multi-Language**: Built-in internationalization (i18n) support for various languages

## 📦 Installation

### Using pip

```bash
pip install wt-resource-tool
```

### Using poetry

```bash
poetry add wt-resource-tool
```

### Using uv

```bash
uv add wt-resource-tool
```

## 🚀 Quick Start

### Prerequisites

Before using WTRT, you need to clone the [War-Thunder-Datamine](https://github.com/gszabi99/War-Thunder-Datamine) repository locally:

```bash
git clone https://github.com/gszabi99/War-Thunder-Datamine.git
```

### Recommended: Using the Parser Directly

The `WTResourceToolParser` is the **recommended approach** for most use cases. It provides direct access to parsed data without memory overhead, giving you full control over how to store and query the data.

```python
import asyncio
from wt_resource_tool import WTResourceToolParser

async def main():
    # Initialize parser with repo path
    parser = WTResourceToolParser(repo_path="/path/to/War-Thunder-Datamine")
    
    # Get current game version
    version = await parser.current_game_version()
    print(f"Current game version: {version}")
    
    # Parse player titles
    title_data = await parser.parse_player_title()
    print(f"Total titles: {len(title_data.titles)}")
    
    # Find a specific title
    god_of_war = next(
        (t for t in title_data.titles if t.title_id == "title_god_of_war"),
        None
    )
    if god_of_war:
        print(f"Title: {god_of_war.name_i18n.english}")
        print(f"Chinese: {god_of_war.name_i18n.chinese}")
    
    # Parse player medals
    medal_data = await parser.parse_player_medal()
    print(f"Total medals: {len(medal_data.medals)}")
    
    # Filter medals by country
    french_medals = [m for m in medal_data.medals if m.country == "france"]
    for medal in french_medals[:3]:
        print(f"{medal.medal_id}: {medal.name_i18n.english}")
        print(f"  Icon: {medal.get_image_cdn_url()}")
    
    # Parse vehicle data
    vehicle_data = await parser.parse_vehicle_data()
    print(f"Total vehicles: {len(vehicle_data.vehicles)}")
    
    # Find a specific vehicle
    ztz99a = next(
        (v for v in vehicle_data.vehicles if v.vehicle_id == "cn_ztz_99a"),
        None
    )
    if ztz99a:
        print(f"Vehicle: {ztz99a.name_shop_i18n.english if ztz99a.name_shop_i18n else 'N/A'}")
        print(f"Rank: {ztz99a.rank}")
        print(f"Country: {ztz99a.country}")

asyncio.run(main())
```

**Why use the Parser?**

- ✅ Full control over data storage and querying logic
- ✅ No memory overhead from built-in storage
- ✅ Integrate with your own database or caching system
- ✅ Perfect for custom filtering and processing pipelines

### Alternative: Memory Storage for Quick Queries

If you need a simple, ready-to-use solution with built-in querying capabilities, use `WTResourceToolMemory`:

```python
import asyncio
from wt_resource_tool import WTResourceToolMemory

async def main():
    # Initialize the tool
    resource_tool = WTResourceToolMemory()
    
    # Parse and load data into memory
    await resource_tool.parse_and_load_data(
        data_types=["player_title", "player_medal", "vehicle"],
        local_repo_path="/path/to/War-Thunder-Datamine",
    )
    
    # Use built-in search methods
    title = await resource_tool.get_player_title("title_god_of_war")
    if title:
        print(f"Title: {title.name_i18n.english}")
    
    # Search with filters
    french_medals = await resource_tool.search_player_medal(country="france")
    print(f"French medals: {len(french_medals)}")
    
    # Get vehicle data
    vehicle = await resource_tool.get_vehicle("cn_ztz_99a")
    if vehicle:
        print(f"Vehicle: {vehicle.name_shop_i18n.english if vehicle.name_shop_i18n else 'N/A'}")

asyncio.run(main())
```

**When to use Memory Storage:**

- 💡 Quick prototyping and testing
- 💡 Simple applications with straightforward querying needs
- 💡 You want built-in search and filter functionality
- 💡 Memory usage is not a concern

## 📚 Available Data Types

> [!NOTE]
> More data types will be added in future releases. Data structures may change as the project evolves. Stay tuned!

### Player Titles

Access all player titles in the game with full localization support.

```python
# Get all titles
titles = await resource_tool.search_player_title()

# Get specific title by ID
title = await resource_tool.get_player_title("title_god_of_war", game_version="latest")
```

**Available fields**: `title_id`, `name_i18n`, `game_version`

### Player Medals

Access all player medals with localization and image URLs at different sizes.

```python
# Search all medals
medals = await resource_tool.search_player_medal()

# Search by country
french_medals = await resource_tool.search_player_medal(country="france")

# Get medal with images
medal = await resource_tool.get_player_medal("fr_liberated_medal")
icon_url = medal.get_image_cdn_url()
ribbon_url = medal.get_image_cdn_url(mode="ribbon")
```

**Available fields**: `medal_id`, `country`, `name_i18n`, `desc_i18n`, `game_version`, image URLs

### Vehicle Data

Access comprehensive vehicle data including stats, localization, and images.

```python
# Get all vehicles
vehicles = await resource_tool.search_vehicle()

# Search by country
chinese_vehicles = await resource_tool.search_vehicle(country="china")

# Get specific vehicle
vehicle = await resource_tool.get_vehicle("cn_ztz_99a")
icon_url = vehicle.get_icon_cdn_url()
```

**Available fields**: `vehicle_id`, `country`, `rank`, `economic_rank_historical`, `speed`, multiple name localizations (`name_shop_i18n`, `name_0_i18n`, etc.), `game_version`, and more

## 📖 Examples

Check out the [playground](playground) folder for more comprehensive examples, including:

- [`example_memory_tool.ipynb`](playground/example_memory_tool.ipynb): Jupyter notebook demonstrating all major features

## ⚙️ Requirements

- Python >= 3.12
- Dependencies: `pydantic`, `httpx`, `pandas`, `loguru`, and more (see `pyproject.toml`)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.

## 🙏 Credits

Special thanks to [War-Thunder-Datamine](https://github.com/gszabi99/War-Thunder-Datamine) for providing the original data!

## 📮 Contact

- Author: axiangcoding
- Email: <axiangcoding@gmail.com>

---

Made with ❤️ for the War Thunder community
