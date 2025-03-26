"""
Base configuration classes.
"""

from configparser import ConfigParser


class SectionConfig(object):
    """
    Config object that has an Attribute
    for each key in the given section.
    """

    def __init__(self, config):
        """
        :param config: Configuration object.
        :type config: configparser.ConfigParser
        """
        for attr in config:
            setattr(self, attr, config[attr])


class HousingInsightsConfig(object):
    """
    Thin wrapper around config parser that returns
    a simple SectionConfig.
    """

    def __init__(self, config_file):
        self.parser = ConfigParser()
        self.parser.read(config_file)

    def get_section(self, section):
        """
        :param section: Section name to return.
        :type  section: String

        :returns: SectionConfig object.
        :rtype: SectionConfig.
        """
        section = self.parser[section]
        return SectionConfig(section)
