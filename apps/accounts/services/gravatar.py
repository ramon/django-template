import hashlib
from tempfile import NamedTemporaryFile
from typing import Any
from urllib.parse import urlencode
from urllib.request import urlopen

from django.core.files import File


def get_avatar_from_url(url: str) -> File[Any]:
    """
    Retrieves an avatar image from the specified URL, stores it in a temporary
    file, and returns the file object.

    This function opens the given URL, downloads the content, and writes it
    into a temporary file. The temporary file is then wrapped as a File object
    and returned with the name extracted from the URL.

    Args:
        url: A string representing the URL of the avatar image to be retrieved.

    Returns:
        File: A File object representing the downloaded avatar image.

    Raises:
        AssertionError: If the HTTP response status from the URL is not 200.
    """
    # sem context manager de proposito: o arquivo precisa seguir aberto para o caller.
    img_tmp = NamedTemporaryFile(delete=True)  # noqa: SIM115

    with urlopen(url) as uo:
        assert uo.status == 200
        img_tmp.write(uo.read())
        img_tmp.flush()

    return File(img_tmp, name=url.split("/")[-1])


def gravatar_url(email: str, size: int = 40) -> str:
    """
    Generate a Gravatar URL for the given email address.

    This function generates a URL to retrieve the Gravatar image associated with the
    given email address, hashed using SHA-256. The size of the image can also be
    specified.

    Args:
        email: The email address to generate the Gravatar URL for.
        size: The desired size of the Gravatar image in pixels. Defaults to 40.

    Returns:
        str: The URL for the generated Gravatar image.
    """
    return "https://www.gravatar.com/avatar/{hash}?{query}".format(
        hash=hashlib.sha256(email.lower().encode("utf-8")).hexdigest(),
        query=urlencode({"s": str(size)}),
    )
