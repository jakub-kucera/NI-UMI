
SCP_AUSTRALIA_MAP = {
    "WA": ["NT", "SA"],
    "NT": ["WA", "SA", "Q"],
    "SA": ["WA", "NT", "Q", "NSW", "V"],
    "Q": ["NT", "SA", "NSW"],
    "NSW": ["Q", "SA", "V"],
    "V": ["SA", "NSW"],
    "T": [],
}


def main():
    SCP_AUSTRALIA_MAP


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
