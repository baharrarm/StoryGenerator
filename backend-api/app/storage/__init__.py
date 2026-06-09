import os

storage = os.getenv("STORY_STORAGE")
bucket = os.getenv("STORY_BUCKET")
is_prod = os.getenv("APP_ENV") == "prod"

if storage == "local":
    from .local_storage import save_story, load_story, delete_story
elif storage == "s3" or bucket or is_prod:
    from .s3_storage import save_story, load_story, delete_story, presign_get  # noqa
else:
    # default to local if nothing configured
    from .local_storage import save_story, load_story, delete_story