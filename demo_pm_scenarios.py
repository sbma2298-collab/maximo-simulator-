import runpy

from run_mbo_script import (
    ROOT,
    MaximoStyleMbo,
    AutomationDispatcher,
    Event,
    Service,
    new_work_order,
    InMemoryRepository,
    SavePipeline,
)


SCRIPT_PATH = ROOT / "maximo_scripts" / "WORKORDER_PM_COMPLETE.py"


def run_scenario(
    name,
    worktype,
    status,
    description,
    expected_description=None,
    expect_error=False,
):
    dispatcher = AutomationDispatcher()
    repository = InMemoryRepository()
    service = Service()

    def run_practice_script(local_mbo, runtime_service):
        runpy.run_path(
            str(SCRIPT_PATH),
            init_globals={
                "mbo": MaximoStyleMbo(local_mbo),
                "service": runtime_service,
            },
        )

    # These lines belong in run_scenario(), NOT run_practice_script().
    dispatcher.register("WORKORDER", Event.BEFORE_SAVE, run_practice_script)
    pipeline = SavePipeline(dispatcher, repository, service)

    work_order = new_work_order(
        "1001",
        description,
        worktype=worktype,
    )
    work_order.set_value("STATUS", status)

    try:
        pipeline.save(work_order)

        if expect_error:
            raise AssertionError(
                "Expected completion to be blocked, but save succeeded"
            )

        saved = repository.get("WORKORDER", "1001")
        actual_description = saved["DESCRIPTION"]

        if actual_description != expected_description:
            raise AssertionError(
                f"Expected {expected_description!r}, "
                f"got {actual_description!r}"
            )

        print(f"PASS: {name} | saved description: {actual_description!r}")

    except ValueError as error:
        if not expect_error:
            raise

        print(f"PASS: {name} | blocked: {error}")


def main():
    if not SCRIPT_PATH.is_file():
        raise FileNotFoundError(SCRIPT_PATH)

    run_scenario(
        "PM completion with valid description",
        "PM", "COMP", "Inspect pump",
        expected_description="Inspect pump",
    )

    run_scenario(
        "PM completion trims spaces",
        "PM", "COMP", "  Inspect pump  ",
        expected_description="Inspect pump",
    )

    run_scenario(
        "PM completion blocks empty description",
        "PM", "COMP", "",
        expect_error=True,
    )

    run_scenario(
        "PM completion blocks spaces-only description",
        "PM", "COMP", "   ",
        expect_error=True,
    )

    run_scenario(
        "Non-PM work order is unaffected",
        "CM", "COMP", " Repair pump",
        expected_description=" Repair pump",
    )

    run_scenario(
        "PM not being completed is unaffected",
        "PM", "WAPPR", " Inspect pump",
        expected_description=" Inspect pump",
    )


if __name__ == "__main__":
    main()