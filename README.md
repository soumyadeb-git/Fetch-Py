[![Run Python script](https://github.com/soumyadeb-git/Fetch-Py/actions/workflows/main.yml/badge.svg)](https://github.com/soumyadeb-git/Fetch-Py/actions/workflows/main.yml) 
# Fetch-Py

This repository contains a Python script designed to automate the extraction of specific information from a series of URLs listed in an XML sitemap. The extracted data is stored in a structured JSON format for easy access and further processing.

## Features

- Parses an XML sitemap to retrieve the latest 20 URLs.
- Visits each URL and extracts detailed information from specified sections of the webpage.
- Prioritizes URLs based on predefined criteria.
- Saves the extracted data in a JSON file for easy retrieval and analysis.

## Requirements

- Python 3.x
- The following Python libraries:
  - `requests`
  - `beautifulsoup4`
  - `xml.etree.ElementTree`
  - `json`
  - `re`
  - `os`

## Installation

1. Install Python 3.x if it's not already installed on your machine.
2. Clone the repository to your local machine.
3. Navigate to the repository directory.
4. Install the required Python libraries:

   ```bash
   pip install requests beautifulsoup4
   ```

## Usage

To run the script and extract the data:

1. Ensure you are in the repository directory.
2. Execute the script:

   ```bash
   python data.py  # Replace with the name of your script file
   ```

The script will fetch the latest 10 URLs from the sitemap, visit each URL, extract the required data, and save it to a file named `data1.json` in the `/data/` directory.

## Automation with GitHub Actions

This repository is set up to automate the execution of the script using GitHub Actions. The workflow is configured to run daily at midnight and on every push to the `main` branch. The results are uploaded as an artifact for easy access.

### GitHub Actions Workflow

The GitHub Actions workflow file is located at `.github/workflows/main.yml`. It performs the following steps:

1. Check out the repository.
2. Set up Python.
3. Installs the required dependencies.
4. Runs the script.
5. Upload the resulting JSON file as an artifact.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Contact

For any inquiries or issues, please open an issue on the repository or contact the maintainers directly.

---

By following these instructions, you should be able to set up and run the script, as well as automate the process using GitHub Actions. If you have any questions or need further assistance, feel free to reach out.
