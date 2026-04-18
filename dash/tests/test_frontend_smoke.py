from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import shutil

import pandas as pd
import pytest


HAS_CHROMEDRIVER = shutil.which("chromedriver") is not None
HAS_CHROME = any(
    shutil.which(binary) is not None
    for binary in ("google-chrome", "chromium", "chromium-browser", "chrome")
)

requires_chrome = pytest.mark.skipif(
    not (HAS_CHROMEDRIVER and HAS_CHROME),
    reason="Dash UI tests require chromedriver and a Chrome/Chromium browser in PATH",
)


def load_dash_module():
    module_path = Path(__file__).resolve().parents[2] / "dash" / "app.py"
    spec = spec_from_file_location("dashboard_app", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load dash app module")

    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_build_figure_changes_when_region_changes():
    app_module = load_dash_module()

    df = pd.DataFrame(
        {
            "date": pd.to_datetime(["2021-01-01", "2021-01-01", "2021-01-02", "2021-01-02"]),
            "sales": [100.0, 50.0, 40.0, 60.0],
            "region": ["north", "south", "north", "south"],
        }
    )

    all_regions_fig = app_module.build_figure(df, "all")
    north_fig = app_module.build_figure(df, "north")

    assert "All Regions" in all_regions_fig.layout.title.text
    assert "North" in north_fig.layout.title.text
    assert list(all_regions_fig.data[0]["y"]) != list(north_fig.data[0]["y"])


@requires_chrome
def test_header_is_present(dash_duo):
    app_module = load_dash_module()

    dash_duo.start_server(app_module.app)
    dash_duo.wait_for_text_to_equal("h1", "Pink Morsel Sales Timeline")


@requires_chrome
def test_visualiser_is_present(dash_duo):
    app_module = load_dash_module()

    dash_duo.start_server(app_module.app)
    dash_duo.wait_for_element("#sales-chart")


@requires_chrome
def test_region_picker_buttons_are_present(dash_duo):
    app_module = load_dash_module()

    dash_duo.start_server(app_module.app)

    dash_duo.wait_for_text_to_equal("#region-north", "North")
    dash_duo.wait_for_text_to_equal("#region-east", "East")
    dash_duo.wait_for_text_to_equal("#region-south", "South")
    dash_duo.wait_for_text_to_equal("#region-west", "West")
    dash_duo.wait_for_text_to_equal("#region-all", "All")
