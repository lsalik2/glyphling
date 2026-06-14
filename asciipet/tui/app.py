# asciipet/tui/app.py
from textual.app import App, ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Static, Footer, Input

from asciipet.core.events import EventType
from asciipet.core.simulation import NEED_KEYS

def _bar(value: float, width: int = 10) -> str:
    filled = int(round(max(0.0, min(100.0, value)) / 100 * width))
    return "#" * filled + "-" * (width - filled)

class RenameScreen(ModalScreen):
    def compose(self) -> ComposeResult:
        yield Input(placeholder="new name", id="rename-input")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.dismiss(event.value.strip())

class AsciiPetApp(App):
    CSS = "#pet { height: auto; padding: 1 2; } #stats { height: auto; padding: 0 2; }"
    BINDINGS = [
        ("f", "feed", "Feed"),
        ("p", "play", "Play"),
        ("c", "clean", "Clean"),
        ("r", "rest", "Rest"),
        ("e", "praise", "Pet"),
        ("n", "rename", "Rename"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self, session):
        super().__init__()
        self.session = session
        self.frame = 0

    def compose(self) -> ComposeResult:
        yield Static(id="pet", markup=False)
        yield Static(id="stats", markup=False)
        yield Footer()

    def on_mount(self) -> None:
        self.set_interval(0.25, self._animate)
        self.set_interval(2.0, self._tick)
        self._refresh()

    def _animate(self) -> None:
        self.frame += 1
        self.query_one("#pet", Static).update(self.session.render_frame(self.frame))

    def _tick(self) -> None:
        self.session.tick()
        self._refresh()

    def _refresh(self) -> None:
        self.query_one("#pet", Static).update(self.session.render_frame(self.frame))
        st = self.session.state
        lines = [f"{self.session.spec.name}  ({st.stage})   mood: {st.mood}"]
        for key in NEED_KEYS:
            lines.append(f"{key:<11}{_bar(st.needs[key])}")
        lines.append(f"{'health':<11}{_bar(st.health)}   bond {_bar(st.bond)}")
        self.query_one("#stats", Static).update("\n".join(lines))

    def _do(self, event_type: EventType) -> None:
        self.session.action(event_type)
        self._refresh()

    def action_feed(self) -> None: self._do(EventType.FEED)
    def action_play(self) -> None: self._do(EventType.PLAY)
    def action_clean(self) -> None: self._do(EventType.CLEAN)
    def action_rest(self) -> None: self._do(EventType.REST)
    def action_praise(self) -> None: self._do(EventType.PRAISE)

    def action_rename(self) -> None:
        def apply(name: str | None) -> None:
            if name:
                self.session.action(EventType.RENAME, {"name": name})
                self._refresh()
        self.push_screen(RenameScreen(), apply)
