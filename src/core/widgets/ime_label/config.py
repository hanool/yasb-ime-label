"""Configuration models for the ImeLabelWidget.

Mirrors the options of YASB's language widget and adds ``label_maps``, which
build custom ``{mapped[...]}`` values from ``lang`` and ``ime`` data. Model
names are prefixed with ``ImeLabel`` so they cannot collide with the ones in
``core.validation``.
"""

from pydantic import Field

from core.validation.widgets.base_model import (
    CallbacksConfig,
    CustomBaseModel,
    KeybindingConfig,
)


class ImeLabelMenuConfig(CustomBaseModel):
    blur: bool = True
    round_corners: bool = True
    round_corners_type: str = "normal"
    border_color: str = "system"
    alignment: str = "right"
    direction: str = "down"
    offset_top: int = 6
    offset_left: int = 0
    layout_icon: str = "\uf11c"
    show_layout_icon: bool = True


class ImeLabelCallbacksConfig(CallbacksConfig):
    on_left: str = "toggle_label"


class ImeLabelMatchConfig(CustomBaseModel):
    lang: dict[str, str | int | bool | None] = {}
    ime: dict[str, str | int | bool | None] = {}


class ImeLabelRuleConfig(CustomBaseModel):
    match: ImeLabelMatchConfig = ImeLabelMatchConfig()
    value: str


class ImeLabelMapConfig(CustomBaseModel):
    default: str = ""
    rules: list[ImeLabelRuleConfig] = []


class ImeLabelConfig(CustomBaseModel):
    label: str = "{lang[language_code]}-{lang[country_code]}"
    label_alt: str = "{lang[full_name]}"
    update_interval: int = Field(default=5, ge=1, le=3600)
    class_name: str = ""
    label_maps: dict[str, ImeLabelMapConfig] = {}
    language_menu: ImeLabelMenuConfig = ImeLabelMenuConfig()
    keybindings: list[KeybindingConfig] = []
    callbacks: ImeLabelCallbacksConfig = ImeLabelCallbacksConfig()
