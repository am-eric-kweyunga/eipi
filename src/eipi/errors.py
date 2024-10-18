class EipiError(Exception):
    """Base class for Eipi exceptions"""

    pass


class EipiParserError(Exception):
    """Exception raised for errors in the parser"""

    pass


class EipiConfigError(Exception):
    """Exception raised for errors in the config file"""

    pass


class EipiTemplateError(Exception):
    """Exception raised for errors in the template file"""

    pass


class DatabaseError(Exception):
    """Exception raised for errors in the database"""

    pass
