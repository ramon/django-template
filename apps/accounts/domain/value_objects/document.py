from typing import Self

from pydantic import BaseModel, Field, computed_field, model_validator
from stdnum import exceptions as stdnum_exceptions
from stdnum.br import cpf as br_cpf
from stdnum.us import ssn as us_ssn

#: Nationalities with a checksum-validated national document. Every other
#: nationality falls back to an unvalidated passport number -- the project isn't
#: prepared to validate every country's document format yet.
NATIONALITY_DOCUMENT_TYPES = {
    "BR": "cpf",
    "US": "ssn",
}
FALLBACK_DOCUMENT_TYPE = "passport"


class Document(BaseModel):
    """
    A person's official identity document, typed and validated by nationality.

    Brazilian and US nationalities map to a specific, checksum-validated document
    (CPF and SSN respectively). Every other nationality falls back to a passport
    number, only checked for presence -- not format, since the project isn't
    prepared to validate every country's document yet.

    Attributes:
        nationality: ISO 3166-1 alpha-2 country code the document was issued
            under.
        value: The document number. Normalized in place: punctuation stripped,
            and, for a supported nationality, replaced by the checksum-validated
            canonical form.
    """

    nationality: str = Field(min_length=2, max_length=2)
    value: str = Field(min_length=1, max_length=20)

    @computed_field
    @property
    def document_type(self) -> str:
        return NATIONALITY_DOCUMENT_TYPES.get(self.nationality.upper(), FALLBACK_DOCUMENT_TYPE)

    @model_validator(mode="after")
    def normalize(self) -> Self:
        document_type = self.document_type

        try:
            if document_type == "cpf":
                normalized = br_cpf.validate(self.value)
            elif document_type == "ssn":
                normalized = us_ssn.validate(self.value)
            else:
                normalized = "".join(char for char in self.value if char.isalnum()).upper()
                if not normalized:
                    raise ValueError(
                        "Passport number must have at least one alphanumeric character."
                    )
        except stdnum_exceptions.ValidationError as exc:
            raise ValueError(f"Invalid {document_type} number.") from exc

        object.__setattr__(self, "value", normalized)
        return self
