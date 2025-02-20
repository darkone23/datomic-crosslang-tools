
class TransitCacheControl:
    """
    private static final int CACHE_CODE_DIGITS = 44;
    private static final int BASE_CHAR_INDEX = 48;
    private static final String SUB_STR = "^";

    private String indexToCode(int index) {
        int hi = index / CACHE_CODE_DIGITS;
        int lo = index % CACHE_CODE_DIGITS;
        if (hi == 0) {
            return SUB_STR + (char)(lo + BASE_CHAR_INDEX);
        } else {
            return SUB_STR + (char)(hi + BASE_CHAR_INDEX) + (char)(lo + BASE_CHAR_INDEX);
        }
    }

    private int codeToIndex(String s) {
        int sz = s.length();
        if (sz == 2) {
            return ((int)s.charAt(1) - WriteCache.BASE_CHAR_INDEX);
        } else {
            return (((int)s.charAt(1) - WriteCache.BASE_CHAR_INDEX) * WriteCache.CACHE_CODE_DIGITS) +
                    ((int)s.charAt(2) - WriteCache.BASE_CHAR_INDEX);
        }
    }
    """

    CACHE_CODE_DIGITS = 44
    BASE_CHAR_INDEX = 48
    SUB_STR = "^"
    MAX_CACHE_SIZE = CACHE_CODE_DIGITS * CACHE_CODE_DIGITS

    def __init__(self):
        self.reset()
        self.enforce = True

    def set_enforce(self, enforce: bool):
        # print("Setting cache enforce to:", enforce)
        self.enforce = enforce

    def reset(self):
        # print("Initializing fresh cache stack")
        self.cache = {}
        self.cursor = 0

    def ack_cache_control(self, item: list):
        # print("thanks for popping", self.cursor, len(self.cache), item)
        if self.enforce:
            cursor = self.cache[item]
            del self.cache[item]
            return cursor

    def syn_cache_control(self, item):
        """We need to grab our ID as soon as we see the cacheable token - not AFTER parsing the token!"""
        if self.enforce:
            if self.cursor > TransitCacheControl.MAX_CACHE_SIZE:
                self.reset()
                print("Resetting the cache due to overflow: you probably want to disable the cache.")
            # print("thanks for adding", self.cursor, len(self.cache), item)
            self.cache[item] = self.cursor
            self.cursor += 1
            # print(self.control_stack)

    @staticmethod
    def index_to_code(index: int) -> str:
        CACHE_CODE_DIGITS = TransitCacheControl.CACHE_CODE_DIGITS
        BASE_CHAR_INDEX = TransitCacheControl.BASE_CHAR_INDEX
        SUB_STR = TransitCacheControl.SUB_STR
        hi: int = int(index / CACHE_CODE_DIGITS)
        lo: int = index % CACHE_CODE_DIGITS
        if hi == 0:
            return SUB_STR + chr(lo + BASE_CHAR_INDEX)
        else:
            return SUB_STR + chr(hi + BASE_CHAR_INDEX) + chr(lo + BASE_CHAR_INDEX)

    @staticmethod
    def code_to_index(s: str) -> int:
        CACHE_CODE_DIGITS = TransitCacheControl.CACHE_CODE_DIGITS
        BASE_CHAR_INDEX = TransitCacheControl.BASE_CHAR_INDEX
        SUB_STR = TransitCacheControl.SUB_STR
        sz = len(s)
        if sz == 2:
            return ord(s[1]) - BASE_CHAR_INDEX
        else:
            return ((ord(s[1]) - BASE_CHAR_INDEX) * CACHE_CODE_DIGITS) + (
                ord(s[2]) - BASE_CHAR_INDEX
            )

