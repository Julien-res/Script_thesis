# Refactored Python Project

## Overview
This project provides a structured approach to processing satellite images using Rayleigh correction and the WiPE algorithm. The code is organized into classes that encapsulate the functionality for applying corrections and generating masks based on satellite image bands.

## Project Structure
```
refactored-python-project
├── src
│   ├── __init__.py
│   ├── main.py
│   ├── rayleigh_correction.py
│   ├── apply_wipe.py
│   └── utils
│       ├── __init__.py
│       └── file_operations.py
├── requirements.txt
└── README.md
```

## Installation
To set up the project, clone the repository and install the required dependencies:

```bash
git clone <repository-url>
cd refactored-python-project
pip install -r requirements.txt
```

## Requirements
The project requires the following Python packages:
- numpy
- esa_snappy

## Usage
To run the application, execute the `main.py` file. You can provide command-line arguments to specify input files, output locations, and processing options.

Example command:
```bash
python src/main.py --input <input_file> --output <output_directory> --resolution 10 --name <output_name>
```

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.