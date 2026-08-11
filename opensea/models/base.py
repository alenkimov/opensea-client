from pydantic import BaseModel, ConfigDict


class OpenSeaModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
