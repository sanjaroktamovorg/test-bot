import enum

class TestType(enum.Enum):
    SIMPLE = "simple"           # Oddiy test
    DTM = "dtm"                 # DTM test
    NATIONAL_CERT = "national_cert"  # Milliy sertifikat test
    OPEN = "open"               # Ochiq (variantsiz) test

class TestCategory(enum.Enum):
    PUBLIC = "public"           # Ommaviy test
    PRIVATE = "private"         # Shaxsiy test

class TestSubject(enum.Enum):
    MATHEMATICS = "mathematics"
    PHYSICS = "physics"
    CHEMISTRY = "chemistry"
    BIOLOGY = "biology"
    HISTORY = "history"
    GEOGRAPHY = "geography"
    LITERATURE = "literature"
    LANGUAGE = "language"
    COMPUTER_SCIENCE = "computer_science"
    OTHER = "other"
