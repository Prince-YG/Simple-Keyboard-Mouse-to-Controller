# Simple Keyboard & Mouse to Controller

Convert keyboard and mouse input into virtual controller input.

This project was created to allow keyboard and mouse controls in applications that only support game controllers. It listens for keyboard and mouse events, translates them using customizable mappings, and sends the corresponding inputs to a virtual controller.

## Features

- Keyboard keys mapped to controller buttons
- Mouse buttons mapped to controller buttons
- Mouse movement converted to analog stick movement
- Easy-to-edit input mappings
- Written in Python
- Modular code structure for easier expansion and maintenance

## How It Works

The program continuously monitors keyboard and mouse input. When an input is detected, it looks up the corresponding controller action and sends that action to a virtual controller.

### Example Mappings

| Input | Controller Action |
|---------|------------------|
| W | Left Stick Up |
| A | Left Stick Left |
| Left Mouse Button | Right Trigger |
| Space | A Button |

Mappings can be customized to fit your own preferences.

## Installation

1. Install the latest [ViGEmBus driver](https://github.com/nefarius/ViGEmBus/releases) driver.
2. Download the latest release of this project from GitHub.
3. Run the application.
4. Configure your mappings if desired.

## Why I Built This

I created this project to learn more about:

- Input handling
- Virtual controller emulation
- Python project architecture
- Event-driven programming

What started as a small learning exercise gradually grew into a fully functional keyboard and mouse to controller converter.

## Current Status

This project is actively being developed. Features, mappings, and performance improvements may change over time as the project evolves.

## Contributing

Pull requests, bug reports, feature requests, and suggestions are welcome.

## License

This project is open source. See the `LICENSE` file for more information.
