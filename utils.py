
def generate_classes(html_classes):
    if not html_classes:
        return []
    return filter(bool, map(lambda u: u.strip(), html_classes.split(',')))
