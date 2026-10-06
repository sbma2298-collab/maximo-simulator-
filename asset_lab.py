from __future__ import annotations

"""Create and test 100 synthetic assets using the existing save pipeline."""

from collections import Counter
from pathlib import Path
import runpy
import sys

# Import the local package without running pip install.
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from maximo_sim.automation.dispatcher import AutomationDispatcher
from maximo_sim.core.events import Event
from maximo_sim.core.mbo import Mbo
from maximo_sim.core.metadata import ObjectMetadata
from maximo_sim.core.service import Service
from maximo_sim.persistence.repository import InMemoryRepository
from maximo_sim.processing.save_pipeline import SavePipeline


SCRIPT = ROOT / "maximo_scripts" / "ASSET_VALIDATE.py"

# Define the fields this local ASSET exercise allows.
ASSET_METADATA = ObjectMetadata(
    object_name="ASSET",
    module_name="ASSET_MANAGEMENT",
    key_attribute="ASSETNUM",
    attributes=frozenset(
        {
            "ASSETNUM",
            "DESCRIPTION",
            "STATUS",
            "SITEID",
            "LOCATION",
            "ASSETTYPE",
            "SERIALNUM",
        }
    ),
)


class MaximoStyleAsset:
    """Expose Maximo-style names to the practice automation script."""

    def __init__(self, local_mbo: Mbo):
        self.local_mbo = local_mbo

    def getString(self, attribute: str) -> str:
        return self.local_mbo.get_string(attribute)

    def isModified(self, attribute: str) -> bool:
        return self.local_mbo.is_modified(attribute)

    def setValue(self, attribute: str, value) -> None:
        self.local_mbo.set_value(attribute, value)


def make_asset(
    number: int,
    *,
    description: str | None = None,
    status: str | None = None,
) -> Mbo:
    """Build one predictable asset for this exercise."""

    asset_types = ("PUMP", "MOTOR", "VALVE", "FAN")
    asset_type = asset_types[(number - 1) % len(asset_types)]
    assetnum = "A{:04d}".format(number)

    # Every 15th asset has a blank status for the script to default.
    # Other every-10th assets start as NOT READY.
    if status is None:
        if number % 15 == 0:
            status = ""
        elif number % 10 == 0:
            status = "NOT READY"
        else:
            status = "OPERATING"

    # Surrounding spaces let us test description cleanup.
    if description is None:
        description = "  {} {} at plant  ".format(
            asset_type.title(),
            number,
        )

    return Mbo(
        ASSET_METADATA,
        {
            "ASSETNUM": assetnum,
            "DESCRIPTION": description,
            "STATUS": status,
            "SITEID": "BEDFORD",
            "LOCATION": "PLANT-{:02d}".format(
                ((number - 1) % 10) + 1
            ),
            "ASSETTYPE": asset_type,
            "SERIALNUM": "SN-{:05d}".format(number),
        },
    )


def build_lab():
    """Register ASSET_VALIDATE.py as an ASSET before-save script."""

    if not SCRIPT.is_file():
        raise FileNotFoundError(
            "Practice script not found: {}".format(SCRIPT)
        )

    dispatcher = AutomationDispatcher()
    repository = InMemoryRepository()
    service = Service()

    def run_asset_script(local_mbo: Mbo, runtime_service: Service):
        # The practice script receives the current asset as "mbo".
        runpy.run_path(
            str(SCRIPT),
            init_globals={
                "mbo": MaximoStyleAsset(local_mbo),
                "service": runtime_service,
            },
        )

    dispatcher.register(
        "ASSET",
        Event.BEFORE_SAVE,
        run_asset_script,
    )

    pipeline = SavePipeline(dispatcher, repository, service)
    return pipeline, repository


def save_unique_asset(
    asset: Mbo,
    pipeline: SavePipeline,
    repository: InMemoryRepository,
) -> None:
    """Reject duplicate asset numbers during the initial load."""

    assetnum = asset.get_string("ASSETNUM")

    if repository.get("ASSET", assetnum) is not None:
        raise ValueError(
            "Duplicate ASSETNUM: {}".format(assetnum)
        )

    pipeline.save(asset)


def expect_rejected(
    label: str,
    asset: Mbo,
    expected_message: str,
    pipeline: SavePipeline,
    repository: InMemoryRepository,
) -> None:
    """Check that an invalid new asset fails and is not saved."""

    assetnum = asset.get_string("ASSETNUM")

    try:
        save_unique_asset(asset, pipeline, repository)
    except ValueError as error:
        assert expected_message in str(error), (
            "{}: unexpected error: {}".format(label, error)
        )
    else:
        raise AssertionError(
            "{}: expected a validation error".format(label)
        )

    assert repository.get("ASSET", assetnum) is None, (
        "{}: invalid asset was saved".format(label)
    )

    print("PASS:", label)


def main() -> None:
    pipeline, repository = build_lab()

    # 1. Create and save 100 valid assets.
    for number in range(1, 101):
        asset = make_asset(number)
        save_unique_asset(asset, pipeline, repository)

    saved_assets = repository.all("ASSET")

    assert len(saved_assets) == 100
    assert len(
        {asset["ASSETNUM"] for asset in saved_assets}
    ) == 100

    print("PASS: created 100 unique assets")

    # 2. Check that the automation script cleaned/defaulted values.
    first = repository.get("ASSET", "A0001")
    fifteenth = repository.get("ASSET", "A0015")
    twentieth = repository.get("ASSET", "A0020")
    last = repository.get("ASSET", "A0100")

    assert first is not None
    assert fifteenth is not None
    assert twentieth is not None
    assert last is not None

    assert first["DESCRIPTION"] == "Pump 1 at plant"
    assert fifteenth["STATUS"] == "OPERATING"
    assert twentieth["STATUS"] == "NOT READY"
    assert last["ASSETNUM"] == "A0100"

    print("PASS: description cleanup and status rules")

    # 3. Check four deliberately invalid assets.
    expect_rejected(
        "blank DESCRIPTION is rejected",
        make_asset(101, description="   "),
        "DESCRIPTION is required",
        pipeline,
        repository,
    )

    bad_site = make_asset(102)
    bad_site.set_value("SITEID", "   ")

    expect_rejected(
        "blank SITEID is rejected",
        bad_site,
        "SITEID is required",
        pipeline,
        repository,
    )

    expect_rejected(
        "invalid STATUS is rejected",
        make_asset(103, status="BROKEN"),
        "Invalid STATUS",
        pipeline,
        repository,
    )

    motor_without_serial = make_asset(106)
    assert motor_without_serial.get_string("ASSETTYPE") == "MOTOR"
    motor_without_serial.set_value("SERIALNUM", "")

    expect_rejected(
        "MOTOR without SERIALNUM is rejected",
        motor_without_serial,
        "SERIALNUM is required",
        pipeline,
        repository,
    )

    # 4. Check duplicate prevention.
    try:
        save_unique_asset(
            make_asset(1),
            pipeline,
            repository,
        )
    except ValueError as error:
        assert "Duplicate ASSETNUM" in str(error)
        print("PASS: duplicate ASSETNUM is rejected")
    else:
        raise AssertionError(
            "Duplicate ASSETNUM should have been rejected"
        )

    # 5. Update an existing asset.
    existing = repository.get("ASSET", "A0001")
    assert existing is not None

    asset_to_update = Mbo(ASSET_METADATA, existing)
    asset_to_update.set_value(
        "DESCRIPTION",
        "  Pump 1 inspected and returned to service  ",
    )

    assert asset_to_update.is_modified("DESCRIPTION")

    # This is an update, so use pipeline.save() rather than
    # save_unique_asset(), which is for new records.
    pipeline.save(asset_to_update)

    updated = repository.get("ASSET", "A0001")
    assert updated is not None
    assert updated["DESCRIPTION"] == (
        "Pump 1 inspected and returned to service"
    )
    assert not asset_to_update.is_modified("DESCRIPTION")

    print("PASS: existing asset updated and changes accepted")

    # 6. Summarize the final repository contents.
    final_assets = repository.all("ASSET")

    by_type = Counter(
        asset["ASSETTYPE"] for asset in final_assets
    )
    by_status = Counter(
        asset["STATUS"] for asset in final_assets
    )

    assert len(final_assets) == 100
    assert by_type == {
        "PUMP": 25,
        "MOTOR": 25,
        "VALVE": 25,
        "FAN": 25,
    }
    assert by_status == {
        "OPERATING": 93,
        "NOT READY": 7,
    }

    print()
    print("FINAL ASSET COUNT:", len(final_assets))
    print("BY TYPE:", dict(sorted(by_type.items())))
    print("BY STATUS:", dict(sorted(by_status.items())))
    print("FIRST ASSET:", repository.get("ASSET", "A0001"))
    print("LAST ASSET:", repository.get("ASSET", "A0100"))
    print()
    print("ALL ASSET LAB CHECKS PASSED")


if __name__ == "__main__":
    main()