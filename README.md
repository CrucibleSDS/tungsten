<div align="center">
    <a align="center" href="https://pypi.org/project/tungsten-sds/">
        <img src="https://raw.githubusercontent.com/Den4200/tungsten/main/assets/tungsten-wide-dark-bg-pad.png" align="center" alt="Tungsten" />
    </a>
    <h1 align="center">Tungsten</h1>
    <p align="center">A material safety data sheet parser.</p>
</div>

## Installation

Tungsten is available on PyPi via pip. To install, run the following command:

```sh
pip install tungsten-sds
```

## Usage Example

```python
import json
from pathlib import Path

from tungsten import SigmaAldrichSdsParser, SdsQueryFieldName, \
    SigmaAldrichFieldMapper

sds_parser = SigmaAldrichSdsParser()
sds_path = Path("CERILLIAN_L-001.pdf")

# Convert PDF file to parsed data
with open(sds_path, "rb") as f:
    sds = sds_parser.parse_to_ghs_sds(f)

field_mapper = SigmaAldrichFieldMapper()

fields = [
    SdsQueryFieldName.PRODUCT_NAME,
    SdsQueryFieldName.PRODUCT_NUMBER,
    SdsQueryFieldName.CAS_NUMBER,
    SdsQueryFieldName.PRODUCT_BRAND,
    SdsQueryFieldName.RECOMMENDED_USE_AND_RESTRICTIONS,
    SdsQueryFieldName.SUPPLIER_ADDRESS,
    SdsQueryFieldName.SUPPLIER_TELEPHONE,
    SdsQueryFieldName.SUPPLIER_FAX,
    SdsQueryFieldName.EMERGENCY_TELEPHONE,
    SdsQueryFieldName.IDENTIFICATION_OTHER,
    SdsQueryFieldName.SUBSTANCE_CLASSIFICATION,
    SdsQueryFieldName.PICTOGRAM,
    SdsQueryFieldName.SIGNAL_WORD,
    SdsQueryFieldName.HNOC_HAZARD,
]

# Serialize parsed data to JSON and dump to a file
with open(sds_path.stem + ".json", "w") as f:
    sds.dump(f)
    # Also print out mapped fields
    for field in fields:
        print(field.name, field_mapper.getField(field, json.loads(sds.dumps())))

```

## License

This work is licensed under MIT. Media assets in the `assets` directory are licensed under a
Creative Commons Attribution-NoDerivatives 4.0 International Public License.

## Notes

This library currently comes bundled with a new build of `tabula-java`, which is also licensed
under MIT, to see the full license, see https://github.com/tabulapdf/tabula-java/blob/master/LICENSE.
