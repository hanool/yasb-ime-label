# yasb-ime-label

An independent [YASB](https://github.com/amnweb/yasb) language widget that
shows the current keyboard layout **and the Windows IME input state** (한/영,
あ/A/カ, ...), with the mapping from IME state to label text kept entirely in
your YASB config.

It is a drop-in replacement for the built-in `yasb.language.LanguageWidget`
plus two additions:

- `{ime[...]}` placeholders exposing the raw Windows IMM32 input mode state
  (open status, conversion mode, sentence mode, `IME_CMODE_*` flags).
- `label_maps`: ordered match rules that turn `lang`/`ime` data into custom
  `{mapped[...]}` values, so Korean/Japanese/Chinese indicators need no
  hardcoded behaviour.

## Why a separate package

YASB ships `core/` and `core/widgets/` without `__init__.py` files, so they
are [PEP 420 namespace packages](https://peps.python.org/pep-0420/). This
project installs only a `core/widgets/ime_label/` fragment, which Python
merges into YASB's own `core.widgets` — no YASB source is modified, so keeping
YASB up to date is just a `git pull`.

**Requirement:** YASB must run from a Python environment you can install into
(a source checkout, venv, or pip install). The MSI/winget bundles are frozen
applications and cannot load additional Python packages.

## Install

Install from the same environment that runs YASB (Windows only, like YASB):

```powershell
pip install D:\dev\yasb-ime-label
```

For development, skip pip and put the fragment on the import path instead
(imports then track your working tree directly):

```powershell
set PYTHONPATH=D:\dev\yasb-ime-label\src;%PYTHONPATH%
```

Note: `pip install -e` (editable) installs an import hook that can shadow the
`core` namespace and break the merge. Use the plain install or `PYTHONPATH`.

## Configure

Replace the `type` of your existing `language` entry; every built-in option
(`label`, `label_alt`, `update_interval`, `language_menu`, `keybindings`,
`callbacks`) keeps working unchanged:

```yaml
language:
  type: "ime_label.language.ImeLabelWidget"
  options:
    label: "{mapped[ime_indicator]}"
    # Use this to observe the values your installed input method reports:
    label_alt: "{lang[language_code]} open={ime[open]} conv={ime[conversion_mode]} native={ime[cmode_native]} kata={ime[cmode_katakana]}"
    update_interval: 1
    label_maps:
      ime_indicator:
        default: "{lang[language_code]}"
        rules:
          # Replace with the values observed from your own input method.
          - match: { lang: { language_code: "ja" }, ime: { cmode_native: false } }
            value: "A"
          - match: { lang: { language_code: "ja" }, ime: { cmode_native: true, cmode_katakana: true } }
            value: "カ"
          - match: { lang: { language_code: "ja" }, ime: { cmode_native: true, cmode_katakana: false } }
            value: "あ"
```

### Placeholders

| Namespace | Fields |
|---|---|
| `{lang[...]}` | same fields as the built-in language widget (`language_code`, `country_code`, `full_name`, `iso_language_code`, ...) |
| `{ime[...]}` | `available`, `open`, `conversion_mode`, `sentence_mode`, `cmode_native`, `cmode_katakana`, `cmode_fullshape`, `cmode_roman`, `cmode_charcode`, `cmode_hanjaconvert`, `cmode_softkbd`, `cmode_noconversion`, `cmode_eudc`, `cmode_symbol`, `cmode_fixed` |
| `{mapped[name]}` | values built by `label_maps.<name>` |

`ime` values are raw IMM32 state. They vary by input method; fields can be
`None` when the active input method does not report them. Rules match by
exact equality — two visible IME modes that report identical values cannot be
told apart through `label_maps`.

### Style

The widget keeps the built-in `language-widget` CSS class (existing themes
work as-is) and adds `ime-label-widget` for widget-specific rules.

## Troubleshooting

- **`Failed to import widget with type ime_label.language.ImeLabelWidget`**
  in `yasb.log`: the package is not installed into the Python running YASB —
  check `pip show yasb-ime-label` from the same interpreter, or use the
  `PYTHONPATH` line above.
- **The label shows the raw template** (e.g. `{mapped[ime_indicator]}`):
  state collection failed and YASB prints the template as-is. Check
  `update_interval`/config errors; on a non-English input method also confirm
  the observed values with the `label_alt` example above.

## Known limitations

- Refresh is timer-based with a minimum of 1 s (`update_interval`); IME state
  changes have no public Windows event to subscribe to.
- Relies on YASB keeping `core`/`core.widgets` namespace packages and on its
  internal widget contract (`validation_schema`, `core.widgets.base`). If an
  upstream update changes either, this package needs a matching update.
- Windows only, like YASB.
