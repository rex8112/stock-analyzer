class StockAnalyzerError(Exception):
    pass


class BadParameters(StockAnalyzerError):
    pass


class ErrorResponse(StockAnalyzerError):
    pass
