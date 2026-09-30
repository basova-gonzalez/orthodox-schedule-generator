"""Julian church calendar, returned as civil Gregorian dates."""
from datetime import date, timedelta


def julian_to_gregorian(year: int, month: int, day: int) -> date:
    """Convert a Julian date through its integer Julian day number."""
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    jdn = day + (153 * m + 2) // 5 + 365 * y + y // 4 - 32083
    a = jdn + 32044
    b = (4 * a + 3) // 146097
    c = a - (146097 * b) // 4
    d = (4 * c + 3) // 1461
    e = c - (1461 * d) // 4
    m = (5 * e + 2) // 153
    return date(100 * b + d - 4800 + m // 10, m + 3 - 12 * (m // 10), e - (153 * m + 2) // 5 + 1)


def pascha(year: int) -> date:
    """Orthodox Pascha using the Julian computus, converted to civil date."""
    a, b, c = year % 4, year % 7, year % 19
    d = (19 * c + 15) % 30
    e = (2 * a + 4 * b - d + 34) % 7
    month, day = divmod(d + e + 114, 31)
    return julian_to_gregorian(year, month, day + 1)


# Nine fixed Twelve Great Feasts, Julian month/day. Pascha is separate.
FIXED_TWELVE = {
    "nativity_theotokos": (9, 8),
    "exaltation_cross": (9, 14),
    "entry_theotokos": (11, 21),
    "nativity_christ": (12, 25),
    "theophany": (1, 6),
    "presentation": (2, 2),
    "annunciation": (3, 25),
    "transfiguration": (8, 6),
    "dormition": (8, 15),
}


def great_feasts(civil_year: int) -> dict[str, date]:
    """All Twelve Great Feasts in a Gregorian year, plus Pascha."""
    if not 1900 <= civil_year <= 2099:
        raise ValueError("Поддерживаются гражданские годы 1900–2099")
    result = {}
    for name, (month, day) in FIXED_TWELVE.items():
        for julian_year in (civil_year - 1, civil_year):
            civil = julian_to_gregorian(julian_year, month, day)
            if civil.year == civil_year:
                result[name] = civil
                break
    easter = pascha(civil_year)
    result.update({
        "entry_jerusalem": easter - timedelta(days=7),
        "ascension": easter + timedelta(days=39),
        "pentecost": easter + timedelta(days=49),
        "pascha": easter,
    })
    return result


def is_highlighted(day: date, additional: set[date] | None = None) -> bool:
    return day.weekday() == 6 or day in great_feasts(day.year).values() or day in (additional or set())
