from sqlalchemy.orm import Session

from app.models.image import Images


def get_image_for_copy(db: Session, image_id: int) -> Images | None:
    return db.query(Images).filter(
        Images.id == image_id,
        Images.is_visible == True,
    ).first()


def copy_image_file(source_key: str, key: str):
    from app.storage import r2

    r2.s3.copy_object(
        Bucket=r2.settings.r2_bucket,
        CopySource={"Bucket": r2.settings.r2_bucket, "Key": source_key},
        Key=key,
    )


def delete_image_file(key: str):
    from app.storage import r2

    r2.delete_object(key)


def create_image_copy(
    db: Session,
    product_id: int,
    key: str,
    position: int,
    is_main: bool,
) -> Images:
    image = Images(
        product_id=product_id,
        key=key,
        position=position,
        is_main=is_main,
    )
    db.add(image)
    db.flush()
    return image
