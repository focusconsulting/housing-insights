from argparse import ArgumentParser

from housinginsights.config.base import HousingInsightsConfig

def main():
    description = "Get csv data from api(s)."
    parser = ArgumentParser(description=description)
    parser.add_argument("--config", "-c", help="Path to the configuration file.")
    parser.add_argument("--output", "-o", help="Output file.")
    parser.add_argument("api", help="Name of the api module.")
    parser.add_argument("method", help="Method of the api to call")
    ns = parser.parse_args()

if __name__ == '__main__':
    main()
