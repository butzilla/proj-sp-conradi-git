
def valid_yn_input(pt):
    """Helper function, to check if input was valid"""
    if pt == 'y' or pt == 'n':
        return True
    else:
        return False


def valid_city_input(city, cities):
    """Helper function, to check if input was valid"""
    if city in cities:
        return True
    else:
        return False


def valid_url_input(zip_url, urls):
    """Helper function, to check if input was valid"""
    if zip_url in urls:
        return True
    else:
        return False