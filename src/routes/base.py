from fastapi import APIRouter


class APIBaseRouter(APIRouter):
    """
    Базовый роут для API
    """

    def __init__(self, *args, **kwargs):
        self.prefix = '/api/v1'
        super().__init__(*args, **kwargs, prefix=self.prefix)
