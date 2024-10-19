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

# adding payload Error class, for internal API calls
class EipiPayloadError(Exception):
    """Exception raised for errors in the payload"""
    pass

class EipiEnvironmentError(Exception):
    """Exception raised for errors in the environment"""
    pass