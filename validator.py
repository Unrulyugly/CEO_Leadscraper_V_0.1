class SearchResult(BaseModel):
    title: str
    snippet: str
    link: str  # Assuming you might want to include the link in the result
    position: int  # Assuming position is also relevant

    @validator('snippet')
    def must_contain_keywords(cls, value, field):
        keywords = ["CEO", "Chief Executive Officer","Executive Director","Managing Partner","President"]
        if not any(keyword in value for keyword in keywords):            raise ValueError(f"{field.name} must contain one of the following: {keywords}")
        return value
