import re


def convert_to_snake_case(string: str):
    pattern = re.compile(r"(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")
    return pattern.sub("_", string).lower()


def convert_to_camel_case(string: str):
    s = re.sub(r"(_|-)+", " ", string).title().replace(" ", "")

    # Join the string, ensuring the first letter is lowercase
    return "".join([s[0].lower(), s[1:]])
