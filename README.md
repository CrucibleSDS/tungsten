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

### Note

Currently, the version of `tabula-java` (1.0.5) included with `tabula-py` (2.5.1) by default is
inadequate as it does not provide page number metadata. To fix this, you must create a custom build
of the `tabula-java` JAR file. To do this, follow the instructions in the `tabula-java` repository:
https://github.com/tabulapdf/tabula-java#building-from-source .
Commit `50ff2df2e62644260d519e2d875a4db7d87d6746` has been tested to work with Tungsten. To enable
this custom build, set the `TABULA_JAR` environment variable to the path of the JAR file.

## Usage Example

```python
from pathlib import Path

from tungsten import SigmaAldrichSdsParser

sds_parser = SigmaAldrichSdsParser()
sds_path = Path("sigma_aldrich_w4502.pdf")

# Convert PDF file to parsed data
with open(sds_path, "rb") as f:
    sds = sds_parser.parse_to_ghs_sds(f, sds_name=sds_path.stem)

# Serialize parsed data to JSON and dump to a file
with open(sds_path.stem + ".json", "w") as f:
    sds.dump(f)
```

## License

This work is licensed under MIT. Media assets in the `assets` directory are licensed under a
Creative Commons Attribution-NoDerivatives 4.0 International Public License.

## Notes

This library currently comes bundled with a new build of `tabula-java`, which is also licensed
under MIT, to see the full license, see https://github.com/tabulapdf/tabula-java/blob/master/LICENSE.
